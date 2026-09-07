# [H] Open WebUI: Redirect-Bypass SSRF in OAuth `_process_picture_url` (incomplete-fix sibling of CVE-2026-45401)

## Summary
Severity: High
Advisory: GHSA-226f-f24g-524w
CVE: CVE-2026-54008
CWE: CWE-918
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:L/A:N (CVSS_V3)
Published: 2026-06-17
Source: https://github.com/advisories/GHSA-226f-f24g-524w
Type: github-advisory

## Affected
- PyPI: `open-webui` — affected >=0 <0.9.6

## Details
## Summary

`backend/open_webui/utils/oauth.py::_process_picture_url` (v0.9.5, lines 1435-1470) calls `validate_url(picture_url)` on the initial URL only, then invokes `aiohttp.ClientSession.get(picture_url, ...)` without `allow_redirects=False`. aiohttp's default is `allow_redirects=True, max_redirects=10`; the function does not pass the project's `AIOHTTP_CLIENT_ALLOW_REDIRECTS` env constant either. An attacker with a valid OAuth IdP identity can therefore submit a public URL that 302-redirects to an internal address and read the internal response body via the attacker's own `profile_image_url` field.

This is the same redirect-bypass class as CVE-2026-45401 (GHSA-rh5x-h6pp-cjj6), on a 6th call site that the v0.9.5 patch missed. CVE-2026-45401's advisory body enumerates exactly five affected paths â€” `SafeWebBaseLoader._scrape`, `_fetch`, `get_content_from_url`, `load_url_image`, `get_image_base64_from_url` â€” none in `utils/oauth.py`.

## Vulnerable code (v0.9.5)

`backend/open_webui/utils/oauth.py`, lines 1435-1470:

```python
async def _process_picture_url(self, picture_url: str, access_token: str = None) -> str:
    if not picture_url:
        return '/user.png'
    try:
        validate_url(picture_url)                              # initial URL only

        get_kwargs = {}
        if access_token:
            get_kwargs['headers'] = {'Authorization': f'Bearer {access_token}'}
        async with aiohttp.ClientSession(trust_env=True) as session:
            async with session.get(picture_url, **get_kwargs,
                                   ssl=AIOHTTP_CLIENT_SESSION_SSL) as resp:
            #                       ^^^^^^^^^^^ no allow_redirects=False
                if resp.ok:
                    picture = await resp.read()
                    base64_encoded_picture = base64.b64encode(picture).decode('utf-8')
                    guessed_mime_type = mimetypes.guess_type(picture_url)[0]
                    if guessed_mime_type is None:
                        guessed_mime_type = 'image/jpeg'
                    return f'data:{guessed_mime_type};base64,{base64_encoded_picture}'
                ...
```

The function is invoked at `oauth.py:1556` (new-user OAuth signup) and `oauth.py:1536` (existing-user picture update on login). Neither call site re-validates after redirect-following.

`backend/open_webui/retrieval/web/utils.py` (v0.9.5) imports the env constant `AIOHTTP_CLIENT_ALLOW_REDIRECTS` at line 51 and uses it on the five paths patched by CVE-2026-45401. `utils/oauth.py` does not import or reference it.

## Exploitation

**Preconditions:**
- `ENABLE_OAUTH_SIGNUP=true` or `OAUTH_UPDATE_PICTURE_ON_LOGIN=true` (common in production OAuth-IdP deployments)
- Attacker has a valid identity on the configured OAuth IdP (Google, Microsoft, GitHub, or any generic OIDC provider)

**Steps:**

1. Attacker hosts a redirect endpoint at `http://attacker.example/r` on a public IP. `validate_url("http://attacker.example/r")` returns True (`is_global=True` for public IPs).
2. Attacker sets their IdP `picture` claim to `http://attacker.example/r`.
3. Attacker signs in to open-webui via OAuth. open-webui invokes `_process_picture_url("http://attacker.example/r", ...)`.
4. `validate_url` accepts the public URL. `session.get("http://attacker.example/r")` is invoked.
5. attacker.example responds `HTTP/1.1 302 Found\r\nLocation: http://127.0.0.1:11434/api/tags`. (Or `http://169.254.169.254/latest/meta-data/iam/security-credentials/`, RFC1918 internal services, etc.)
6. aiohttp follows the redirect server-side. **No re-validation.**
7. The internal response body is read into `picture`, base64-encoded, and stored as `profile_image_url = "data:image/jpeg;base64,..."` on the attacker's account.
8. Attacker reads back via `GET /api/v1/auths/`. Decode the base64 payload to get the full internal response body.

## Impact

Full-read SSRF, identical read-back primitive to CVE-2026-45338:

- Cloud metadata services (AWS IMDSv1 at `169.254.169.254`, GCP `metadata.google.internal`, Azure IMDS) â†’ IAM credentials, managed-identity tokens
- Localhost-bound services (Ollama at `:11434`, Redis, Elasticsearch, internal Postgres exporters)
- RFC1918 internal infrastructure not exposed to the internet

## Distinction from prior CVEs

| Prior CVE | This finding | Distinguishing fact |
|---|---|---|
| CVE-2026-45338 (GHSA-24c9) | `_process_picture_url` had no `validate_url()` call at all | Fixed in v0.9.0 by adding the call. Ours is the call being insufficient because it doesn't loop over redirect targets. Different mechanism, different fix. |
| CVE-2026-45400 (GHSA-8w7q) | `validate_url()` had urlparse-vs-requests parser disagreement on `\@` chars | Fixed in v0.9.5 by char-blocklist. Ours is post-validation redirect-following â€” orthogonal mechanism. |
| CVE-2026-45401 (GHSA-rh5x) | Five paths in retrieval, routers/images, utils/files, utils/middleware | Parent class. Same CWE-918 redirect-bypass mechanism. `utils/oauth.py::_process_picture_url` is not among the five paths in the parent advisory's "Affected code paths" section. Same class, missed sink. Direct sibling. |

## Suggested fix

```python
async with session.get(
    picture_url,
    **get_kwargs,
    ssl=AIOHTTP_CLIENT_SESSION_SSL,
    allow_redirects=AIOHTTP_CLIENT_ALLOW_REDIRECTS,   # add
) as resp:
```

Or, if redirects must remain enabled by default, wrap in a manual-follow loop that re-invokes `validate_url()` on each `Location` header. This mirrors the fix shape applied to the five paths in CVE-2026-45401.

## Affected versions

Vulnerable: `<= 0.9.5`
Fix: 0.9.6

## References

- CVE-2026-45401 / GHSA-rh5x-h6pp-cjj6 (parent cluster, redirect-bypass on 5 paths)
- CVE-2026-45338 / GHSA-24c9-2m8q-qhmh (original `_process_picture_url` SSRF, patched v0.9.0)
- CVE-2026-45400 / GHSA-8w7q-q5jp-jvgx (`validate_url` parser-disagreement bypass, patched v0.9.5)
- open-webui issue #24560 (corroborates that the v0.9.5 redirect-fix was applied piecemeal across call sites)

## Proof of Concept

End-to-end PoC executed against `ghcr.io/open-webui/open-webui:v0.9.5` in Docker compose. Three services: attacker (OIDC IdP + 302-redirect endpoint on `evil.example.com:9001/redirect`), canary (internal target on `internal-target.local:9002/sentinel`), open-webui v0.9.5.

Fresh-CSPRNG sentinel generated **after** OAuth state-establishing call (per Gate 5.5 oracle protocol): `SSRF-POC-5580111b2a0d7d0c8324bfa92a0d9d09`.

Result:
- `profile_image_url` field after OAuth login: `data:image/jpeg;base64,U1NSRi1QT0MtNTU4MDExMWIyYTBkN2QwYzgzMjRiZmE5MmEwZDlkMDk=`
- Base64 decode: `SSRF-POC-5580111b2a0d7d0c8324bfa92a0d9d09` (byte-for-byte sentinel match)
- Canary log: `!!! SSRF HIT - sentinel served`

Chain confirmed: OAuth login â†’ IdP returns picture claim `evil.example.com:9001/redirect` â†’ `validate_url()` accepts FQDN â†’ `aiohttp.ClientSession.get(...)` follows 302 to `internal-target.local:9002/sentinel` server-side without re-validation â†’ response body base64-encoded into attacker's `profile_image_url` â†’ readable via `GET /api/v1/auths/`.

PoC artifacts (compose, attacker server, canary, run/verify scripts, full transcript) available on request.

## Reporter

Matteo Panzeri â€” GitHub: `matte1782`, contact: `matteo1782@gmail.com`. Requesting CVE credit as **Matteo Panzeri**.

## References
- https://github.com/open-webui/open-webui/security/advisories/GHSA-226f-f24g-524w
- https://github.com/open-webui/open-webui
