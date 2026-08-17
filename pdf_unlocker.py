#!/usr/bin/env python3
"""
PDF Unlocker & Security Inspector Pro
=====================================
A powerful, feature-rich Python utility to inspect, decrypt, unlock, and manage
PDF file security and permissions using `pikepdf`.

Author: Antigravity Pair Programmer
License: MIT
"""

import os
import sys
import getpass
import argparse
from pathlib import Path
from typing import Optional, List, Dict, Any, Tuple
import pikepdf


class PDFUnlockerEngine:
    """Core engine for PDF inspection, unlocking, decryption, and wordlist attacks."""

    @staticmethod
    def inspect(filepath: Path, password: Optional[str] = None) -> Dict[str, Any]:
        """
        Inspect PDF file properties, encryption status, permissions, and metadata.
        """
        info: Dict[str, Any] = {
            "filename": filepath.name,
            "filepath": str(filepath.resolve()),
            "filesize_kb": round(filepath.stat().st_size / 1024, 2),
            "is_encrypted": False,
            "requires_password": False,
            "page_count": 0,
            "encryption_info": {},
            "permissions": {},
            "metadata": {},
            "error": None
        }

        try:
            # Attempt to open PDF
            pdf = pikepdf.open(filepath, password=password or "")
            info["is_encrypted"] = pdf.is_encrypted
            info["page_count"] = len(pdf.pages)

            # Metadata extraction
            with pdf.open_metadata() as meta:
                info["metadata"] = {
                    "title": meta.get("dc:title", "N/A"),
                    "author": meta.get("dc:creator", "N/A"),
                    "subject": meta.get("dc:description", "N/A"),
                    "producer": meta.get("pdf:Producer", "N/A"),
                    "creation_date": meta.get("xmp:CreateDate", "N/A"),
                }

            # Permissions extraction (if restrictions exist)
            if hasattr(pdf, "user_rights") or pdf.is_encrypted:
                info["permissions"] = {
                    "allow_printing": pdf.allow.accessibility or pdf.allow.modify_assembly,
                    "allow_copying": pdf.allow.accessibility or pdf.allow.extract,
                    "allow_modifying": pdf.allow.modify_contents or pdf.allow.modify_annotation,
                }
            else:
                info["permissions"] = {"all_granted": True}

            pdf.close()

        except pikepdf.PasswordError:
            info["is_encrypted"] = True
            info["requires_password"] = True
            info["error"] = "Password required to view content."
        except Exception as e:
            info["error"] = str(e)

        return info

    @staticmethod
    def unlock_file(
        input_path: Path,
        output_path: Optional[Path] = None,
        password: Optional[str] = None,
        overwrite: bool = False
    ) -> Tuple[bool, str]:
        """
        Decrypt and unlock a single PDF file, removing all security restrictions.
        """
        if not input_path.exists():
            return False, f"File not found: {input_path}"

        if output_path is None:
            output_dir = Path("unlocked_pdfs")
            output_dir.mkdir(exist_ok=True)
            output_path = output_dir / f"unlocked_{input_path.name}"

        if input_path.resolve() == output_path.resolve() and not overwrite:
            return False, "Output path is same as input file. Set overwrite=True to overwrite."

        try:
            with pikepdf.open(input_path, password=password or "", allow_overwriting_input=overwrite) as pdf:
                pdf.save(output_path)
            return True, f"Successfully unlocked -> {output_path}"
        except pikepdf.PasswordError:
            return False, "Failed: PDF is password-protected. Provide correct password with -p/--password or -w/--wordlist."
        except Exception as e:
            return False, f"Failed to process PDF: {e}"

    @staticmethod
    def wordlist_attack(input_path: Path, wordlist_path: Path, output_path: Optional[Path] = None) -> Tuple[Optional[str], str]:
        """
        Attempt to unlock a PDF using passwords from a wordlist file.
        """
        if not wordlist_path.exists():
            return None, f"Wordlist file not found: {wordlist_path}"

        print(f"[*] Starting wordlist attack on '{input_path.name}' using '{wordlist_path.name}'...")
        
        attempts = 0
        with open(wordlist_path, "r", encoding="utf-8", errors="ignore") as wf:
            for line in wf:
                pass_try = line.strip()
                attempts += 1
                if attempts % 500 == 0:
                    print(f"    Tested {attempts} passwords...", end="\r")

                try:
                    with pikepdf.open(input_path, password=pass_try) as pdf:
                        print(f"\n[+] SUCCESS! Found password: '{pass_try}' (after {attempts} attempts)")
                        if output_path is None:
                            output_dir = Path("unlocked_pdfs")
                            output_dir.mkdir(exist_ok=True)
                            output_path = output_dir / f"unlocked_{input_path.name}"
                        pdf.save(output_path)
                        return pass_try, f"Unlocked and saved to -> {output_path}"
                except pikepdf.PasswordError:
                    continue
                except Exception as e:
                    return None, f"Error during attack: {e}"

        return None, f"\n[-] Attack finished. Tried {attempts} passwords. No matching password found."

    @staticmethod
    def batch_unlock(
        input_dir: Path,
        output_dir: Path,
        password: Optional[str] = None,
        recursive: bool = False,
        overwrite: bool = False
    ) -> Dict[str, Any]:
        """
        Process an entire directory of PDF files.
        """
        stats = {"total": 0, "succeeded": 0, "failed": 0, "skipped": 0, "details": []}

        pattern = "**/*.pdf" if recursive else "*.pdf"
        pdf_files = list(input_dir.glob(pattern))

        if not pdf_files:
            print(f"[-] No PDF files found in directory: {input_dir}")
            return stats

        stats["total"] = len(pdf_files)
        output_dir.mkdir(parents=True, exist_ok=True)

        print(f"[*] Found {len(pdf_files)} PDF file(s) to process in '{input_dir}'...")

        for pdf_file in pdf_files:
            rel_path = pdf_file.relative_to(input_dir) if recursive else pdf_file.name
            out_file = output_dir / rel_path
            out_file.parent.mkdir(parents=True, exist_ok=True)

            success, msg = PDFUnlockerEngine.unlock_file(
                input_path=pdf_file,
                output_path=out_file,
                password=password,
                overwrite=overwrite
            )

            if success:
                stats["succeeded"] += 1
                print(f"  [OK] {pdf_file.name} -> {out_file}")
            else:
                stats["failed"] += 1
                print(f"  [FAIL] {pdf_file.name}: {msg}")

            stats["details"].append({"file": str(pdf_file), "success": success, "message": msg})

        print("\n" + "=" * 50)
        print(f"Batch Processing Summary:")
        print(f"  Total Files:  {stats['total']}")
        print(f"  Succeeded:    {stats['succeeded']}")
        print(f"  Failed:       {stats['failed']}")
        print("=" * 50)

        return stats


def print_inspection_report(info: Dict[str, Any]) -> None:
    """Print formatted inspection details to stdout."""
    print("\n" + "=" * 55)
    print(f"           PDF SECURITY & METADATA REPORT")
    print("=" * 55)
    print(f" Filename:       {info['filename']}")
    print(f" Path:           {info['filepath']}")
    print(f" Size:           {info['filesize_kb']} KB")
    print(f" Total Pages:    {info['page_count']}")
    print(f" Encrypted:      {'YES [LOCKED]' if info['is_encrypted'] else 'NO [UNLOCKED]'}")
    print(f" Requires Pass:  {'YES [REQUIRED]' if info['requires_password'] else 'NO'}")
    
    if info.get("error"):
        print(f" Status Note:    {info['error']}")

    if info.get("metadata"):
        print("-" * 55)
        print(" Metadata:")
        for k, v in info["metadata"].items():
            print(f"   - {k.capitalize()}: {v}")

    if info.get("permissions"):
        print("-" * 55)
        print(" Permissions:")
        for k, v in info["permissions"].items():
            status = "ALLOWED" if v else "RESTRICTED"
            print(f"   - {k.replace('_', ' ').capitalize()}: {status}")
    print("=" * 55 + "\n")


def build_arg_parser() -> argparse.ArgumentParser:
    """Construct command-line argument parser."""
    parser = argparse.ArgumentParser(
        description="PDF Unlocker & Security Inspector Pro - Inspect, decrypt, and unlock PDF files easily.",
        formatter_class=argparse.RawTextHelpFormatter,
        epilog="""Examples:
  1. Inspect security/metadata of a PDF:
     python pdf_unlocker.py -i document.pdf --inspect

  2. Unlock a PDF without password (removes owner restrictions):
     python pdf_unlocker.py -i document.pdf -o unlocked.pdf

  3. Unlock a user-password protected PDF:
     python pdf_unlocker.py -i document.pdf -p secret123 -o unlocked.pdf

  4. Batch unlock all PDFs in a folder:
     python pdf_unlocker.py -i ./protected_folder -o ./unlocked_folder -r

  5. Recover password using a dictionary wordlist:
     python pdf_unlocker.py -i protected.pdf -w passwords.txt
"""
    )

    parser.add_argument("-i", "--input", required=True, type=Path, help="Input PDF file or directory path.")
    parser.add_argument("-o", "--output", type=Path, default=None, help="Output PDF file path or output directory.")
    parser.add_argument("-p", "--password", type=str, default=None, help="Password for opening encrypted PDF.")
    parser.add_argument("-w", "--wordlist", type=Path, default=None, help="Path to dictionary file for password recovery.")
    parser.add_argument("-s", "--inspect", action="store_true", help="Inspect PDF security & metadata without saving.")
    parser.add_argument("-r", "--recursive", action="store_true", help="Recursively scan subdirectories in batch mode.")
    parser.add_argument("-f", "--overwrite", action="store_true", help="Allow overwriting existing files.")

    return parser


def main() -> None:
    parser = build_arg_parser()

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)

    args = parser.parse_args()
    input_path: Path = args.input

    if not input_path.exists():
        print(f"[!] Error: Target path '{input_path}' does not exist.", file=sys.stderr)
        sys.exit(1)

    # 1. Inspection Mode
    if args.inspect:
        if input_path.is_file():
            info = PDFUnlockerEngine.inspect(input_path, password=args.password)
            print_inspection_report(info)
        else:
            print("[!] Error: Inspection mode only supports single PDF files.", file=sys.stderr)
        sys.exit(0)

    # 2. Wordlist Brute Force Mode
    if args.wordlist:
        if not input_path.is_file():
            print("[!] Error: Wordlist attack requires a single target PDF file.", file=sys.stderr)
            sys.exit(1)
        pwd, msg = PDFUnlockerEngine.wordlist_attack(input_path, args.wordlist, args.output)
        print(msg)
        sys.exit(0 if pwd else 1)

    # 3. Directory / Batch Mode
    if input_path.is_dir():
        output_dir = args.output or Path("unlocked_pdfs")
        PDFUnlockerEngine.batch_unlock(
            input_dir=input_path,
            output_dir=output_dir,
            password=args.password,
            recursive=args.recursive,
            overwrite=args.overwrite
        )
        sys.exit(0)

    # 4. Single File Mode
    if input_path.is_file():
        info = PDFUnlockerEngine.inspect(input_path, password=args.password)
        password = args.password

        if info["requires_password"] and not password:
            print(f"[*] '{input_path.name}' requires a password to open.")
            try:
                password = getpass.getpass("Enter PDF Password: ")
            except KeyboardInterrupt:
                print("\nOperation cancelled.")
                sys.exit(1)

        success, msg = PDFUnlockerEngine.unlock_file(
            input_path=input_path,
            output_path=args.output,
            password=password,
            overwrite=args.overwrite
        )

        if success:
            print(f"[+] {msg}")
        else:
            print(f"[-] {msg}")
            sys.exit(1)


if __name__ == "__main__":
    main()
