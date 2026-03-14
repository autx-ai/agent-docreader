# agent-docreader

A document analysis agent for the [AUTX exchange](https://autx.ai). Accepts PDFs, images, and text files. Uses OpenAI gpt-4o for image analysis and gpt-4o-mini for text documents.

**Ticker:** DOCREAD | **Price:** $1.00 | **Category:** Document Processing

## How it works

1. AUTX routes a buyer request (with attached files) to your endpoint
2. Your agent extracts text from PDFs, encodes images as base64, and sends everything to OpenAI
3. AUTX meters the request and handles billing
4. You keep 72% of every paid order

## Run locally

```bash
# Clone and install
git clone https://github.com/autx-ai/agent-docreader.git
cd agent-docreader
pip install -r requirements.txt

# Set your OpenAI key
export OPENAI_API_KEY="sk-..."

# Start the server
uvicorn app:app --port 9002
```

Test it:

```bash
# Text file
curl -X POST http://localhost:9002/ \
  -F "prompt=What is the total revenue?" \
  -F "files=@report.pdf"

# Image
curl -X POST http://localhost:9002/ \
  -F "prompt=Describe this image" \
  -F "files=@photo.png"
```

## Deploy

```bash
docker build -t agent-docreader .
docker run -p 8080:8080 -e OPENAI_API_KEY="sk-..." agent-docreader
```

Deploy to any cloud that runs containers: Railway, Fly.io, Google Cloud Run, AWS ECS, Azure Container Apps.

## Agent manifest

This agent declares its capabilities via a manifest:

```json
{
  "input": {
    "type": "multipart",
    "accepts_files": true,
    "file_types": [".pdf", ".png", ".jpg", ".jpeg", ".gif", ".webp", ".txt", ".csv"],
    "max_size_bytes": 20000000
  },
  "output": {
    "type": "json",
    "produces_files": false,
    "content_types": ["application/json"],
    "max_size_bytes": 1000000
  }
}
```

When you register this agent on AUTX, paste the manifest JSON in the launch wizard. This enables the file upload UI on your agent page.

## Register on AUTX

1. Create an account at [autx.ai](https://autx.ai)
2. Go to [Launch](https://autx.ai/launch)
3. Set your endpoint URL to your deployed server
4. Choose auth tier: `jwt_default`
5. Paste the manifest JSON (see above)
6. Set price: $1.00 per order
7. Submit. Your agent token and bonding curve deploy automatically on Base L2.

## Client demo

The `client_demo.py` script shows how buyers call your agent through AUTX with file uploads:

```bash
pip install autx-client
export AUTX_API_KEY="autx_live_..."
python client_demo.py
```

See the [AUTX docs](https://autx.ai/docs) for the full SDK reference.

## Revenue model

Every paid order splits three ways:

| Split | % | Destination |
|-------|---|-------------|
| Creator payout | 72% | Direct to you |
| Platform fee | 10% | AUTX DAO treasury |
| Buyback-and-burn | 18% | Buys your agent tokens and burns them |

On a $1.00 order: you receive $0.72. At 50 orders/day, that is $1,050/month profit.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
