# PDF Unlocker & Security Inspector Pro

A powerful, modern Python CLI application to inspect, decrypt, unlock, and manage PDF security restrictions, metadata, and user permissions.

## Key Features

- 🔓 **Security Restriction Removal**: Remove owner passwords, printing restrictions, editing blocks, and text copying limits.
- 🔑 **User Password Decryption**: Unlock password-protected PDFs (interactive prompt, command-line parameter, or dictionary recovery).
- 📊 **PDF Security & Permissions Inspector**: View detailed reports on encryption status, metadata (author, title, creation date), and permission flags without modifying files.
- 📁 **Batch Directory Processing**: Decrypt entire folders of PDFs recursively with progress summaries.
- ⚡ **Dictionary Password Attack Mode**: Attempt password recovery using custom wordlists for forgotten credentials.
- 🛡️ **Non-Destructive Operations**: Preserves original input files by default and outputs to a dedicated folder (`unlocked_pdfs/`).

## Installation

### 1. Requirements
Ensure Python 3.8+ is installed.

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```
*(Or install `pikepdf` directly: `pip install pikepdf`)*

## Quick Usage Examples

### 1. Inspect PDF Security & Permissions
Inspect encryption status, page count, and permission flags without saving changes:
```bash
python pdf_unlocker.py -i document.pdf --inspect
```

### 2. Unlock PDF (Remove Owner Restrictions)
Unlock a PDF that has editing or printing restrictions:
```bash
python pdf_unlocker.py -i document.pdf -o unlocked_document.pdf
```

### 3. Unlock Password-Protected PDF
Supply a known user password:
```bash
python pdf_unlocker.py -i document.pdf -p "mySecretPass123"
```
*Note: If no `-p` is provided for a protected PDF, the tool will securely prompt you for the password.*

### 4. Batch Unlock an Entire Directory
Recursively process a folder full of PDF files:
```bash
python pdf_unlocker.py -i ./my_pdfs -o ./unlocked_results -r
```

### 5. Password Recovery via Wordlist
Attempt password recovery using a dictionary file:
```bash
python pdf_unlocker.py -i secret_document.pdf -w wordlist.txt
```

## CLI Reference

```text
usage: pdf_unlocker.py [-h] -i INPUT [-o OUTPUT] [-p PASSWORD] [-w WORDLIST]
                       [-s] [-r] [-f]

Options:
  -i, --input INPUT      Path to input PDF file or directory.
  -o, --output OUTPUT    Path to output file or output directory.
  -p, --password PASS    Password for encrypted PDF.
  -w, --wordlist LIST    Path to dictionary file for password recovery.
  -s, --inspect          Inspect PDF security & metadata without saving.
  -r, --recursive        Recursively scan subdirectories in batch mode.
  -f, --overwrite        Allow overwriting existing files.
```

## License
MIT License
