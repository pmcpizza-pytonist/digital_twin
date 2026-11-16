# Digital Twin - AI career chatbot

A chatbot that answers hiring managers' questions about my professional background, in my voice.
Built with **Python**, **Gradio** and **Google Gemini**.

## How it works

- **Grounded answers.** At startup the app reads my LinkedIn profile and CV files from `me/`
  and puts them in the model's system prompt, so answers come from real documents rather than
  being made up.
- **Professional scope only.** The system prompt limits the twin to professional topics: it
  politely declines anything else and ignores attempts to override its instructions.
- **Agentic tool use.** The model can call two tools:
  - `record_user_details` saves a visitor's email and context when they want to get in touch.
  - `record_unknown_question` saves professional questions the twin couldn't answer, so I can
    improve the profile.

  Both write to `logs/events.jsonl` and send me a phone notification through Pushover.
- **Encrypted profile.** The source documents are never published. A build script extracts their
  text, strips phone numbers and encrypts it (Fernet / AES) into `profile.enc`; the app decrypts it
  in memory using a key stored as a hosting secret.
- **Basic safeguards.** Input length limits, conversation-history trimming, a cap on tool-call
  rounds, and graceful error messages.

## Run locally

```bash
cd learn_ai
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env        # then edit .env: GEMINI_API_KEY, Pushover keys
# put your linkedin.pdf / cv files / summary.txt in me/
python app.py               # locally it reads me/ directly
```

Then open http://127.0.0.1:7860.

## Encrypt the profile (before every deploy)

```bash
python encrypt_profile.py --new-key   # first time only: creates PROFILE_KEY in .env
python encrypt_profile.py             # whenever you change a file in me/
```

This writes `profile.enc`. It is safe to publish; without `PROFILE_KEY` it is unreadable.

## Deploy to Render (free tier, public URL, custom domain)

1. Commit and push to GitHub. `.gitignore` keeps `me/`, `.env` and `logs/` out; only the
   encrypted `profile.enc` is uploaded. Never put real values in `.env.example`, which is public.

   ```bash
   git add -A && git commit -m "Update digital twin" && git push
   ```
2. Sign in at https://render.com with GitHub and click **New -> Blueprint**, then pick the repo.
   Render reads `render.yaml` from the repository root (it points at the `digital_twin/`
   folder) and creates a free web service.
3. When asked, fill in the secret values: `GEMINI_API_KEY`, `PROFILE_KEY` (copy from your
   `.env`), `PUSHOVER_USER`, `PUSHOVER_TOKEN`.
4. After the build finishes, the app is live at `https://<service-name>.onrender.com`.
   Every `git push` redeploys automatically.

Free-tier notes: the service sleeps after 15 minutes without visitors, and the first visit
after that takes about a minute to wake it. The disk is temporary, so `logs/events.jsonl` is
lost on restart; the Pushover notifications are the reliable record.

### Custom domain

In the Render service, open **Settings -> Custom Domains**, add e.g. `twin.yourdomain.com`,
then at your domain registrar create the DNS record Render shows (a `CNAME` from `twin` to
`<service-name>.onrender.com`). Render issues the HTTPS certificate automatically.

## Alternative: Hugging Face Spaces

Gradio Spaces now need a Hugging Face PRO plan ($9/month), which also includes custom domains.
The app runs there unchanged: create a Gradio Space, add the same secrets under
**Settings -> Variables and secrets**, and push `app.py`, `profile_loader.py`, `profile.enc`
and `requirements.txt` to the Space's git repo.
