# RapidAPI Hosting & Monetization Guide

Follow this guide to deploy your PDF Unlocker API for free and list it on RapidAPI to start earning revenue per request.

---

## Step 1: Deploy API Server (Free Hosting options)

You can host your API server for free on platforms like **Render**, **Railway**, or **Fly.io**.

### Option A: Deploy on Render.com (Recommended & Free)
1. Sign up / Log into [Render.com](https://render.com).
2. Click **New +** -> **Web Service**.
3. Connect your GitHub repository (`navaneethmng-droid/pdf-unlocker-pro`).
4. Set the following settings:
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
5. Click **Create Web Service**. Render will give you a public URL like:
   `https://pdf-unlocker-pro.onrender.com`

---

## Step 2: List & Monetize on RapidAPI

1. Go to [RapidAPI Studio](https://rapidapi.com/studio) and click **Add New API**.
2. Fill in basic details:
   - **API Name**: `PDF Unlocker & Security API`
   - **Description**: `Fast, reliable API to inspect PDF security attributes and remove encryption/passwords.`
   - **Category**: `Utilities` / `Documents`
3. In **Target Endpoint**:
   - Set Base URL: `https://pdf-unlocker-pro.onrender.com`
4. Add Endpoints:
   - **Endpoint 1**: `POST /api/v1/inspect` (Upload PDF file -> Returns JSON report)
   - **Endpoint 2**: `POST /api/v1/unlock` (Upload PDF file -> Returns unlocked PDF file stream)

---

## Step 3: Configure $0.001 Pricing Plans

In RapidAPI Studio -> **Monetization & Plans**:

1. **Basic Plan ($5/month)**:
   - Monthly Quota: `5,000 requests` (calculates to **$0.001 / request**)
   - Overage Fee: `$0.001 per extra request`

2. **Pro Plan ($20/month)**:
   - Monthly Quota: `25,000 requests` (calculates to **$0.0008 / request**)
   - Overage Fee: `$0.001 per extra request`

3. **Free Tier (Optional)**:
   - Monthly Quota: `50 requests` (Hard cap, no overage) so developers can test your API.

---

## Testing API Locally

To run the API server locally:
```bash
pip install -r requirements.txt
python main.py
```
Open your browser to `http://localhost:8000/docs` for the interactive Swagger API documentation and testing interface.
