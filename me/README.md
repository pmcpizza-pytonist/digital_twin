# Profile documents

Put the documents the digital twin should learn from in this folder.
Every PDF, DOCX, TXT and MD file here (except this README) is loaded at startup.

Suggested files:

- `linkedin.pdf` - LinkedIn profile export (on LinkedIn: your profile -> "Resources" / "More" -> "Save to PDF")
- `cv.pdf` or `cv.docx` - your CV (you can add several, e.g. a Hebrew and an English version)
- `summary.txt` - a few paragraphs in your own words: what you're looking for, what you're proud of,
  how you like to work. This is what makes the twin sound like you.

Privacy: this folder is excluded from git (see .gitignore) and is never published.
For deployment, run `python encrypt_profile.py` to produce the encrypted profile.enc instead.
