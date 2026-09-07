# [H] garminconnect Has Insecure Permission Assignment for Garmin OAuth Token Store

## Summary
Severity: High
Advisory: GHSA-wjhr-76vg-2hvc
CVE: CVE-2026-54447
CWE: CWE-732
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:N (CVSS_V3)
Published: 2026-07-15
Source: https://github.com/advisories/GHSA-wjhr-76vg-2hvc
Type: github-advisory

## Affected
- PyPI: `garminconnect` — affected >=0 <0.3.5

## Details
## Insecure Permission Assignment for Garmin OAuth Token Store

### Summary

`garminconnect` (≤ 0.3.4) wrote its OAuth token store to disk without restricting file-system permissions. Under the default Linux umask (`022`) the token file `garmin_tokens.json` was created world-readable (`0o644`). The file contains the DI **refresh token**, so any other local user on a shared host could read it and obtain persistent, unauthorized access to the victim's Garmin Connect account.

- **Severity:** High
- **Weakness:** CWE-732 (Incorrect Permission Assignment for Critical Resource)
- **Affected versions:** `<= 0.3.4`
- **Patched version:** `0.3.5`

### Details

`Client.dump()` created the token directory and file with no `mode` argument, leaving permissions entirely to the process umask:

```python
def dump(self, path: str) -> None:
    p = Path(path).expanduser()
    if p.is_dir() or not p.name.endswith(".json"):
        p = p / "garmin_tokens.json"
    p.parent.mkdir(parents=True, exist_ok=True)   # no mode=
    p.write_text(self.dumps())                     # no permission restriction
```

The serialized payload includes `di_token`, `di_refresh_token`, and `di_client_id`. The call is in the core library (`Garmin.login(tokenstore=...)` persists tokens this way), and all shipped usage examples default the token store to `~/.garminconnect`.

Under `umask 022` the resulting permissions were:

- token directory → `0o755`
- `garmin_tokens.json` → `0o644` (world-readable)

A separate, unprivileged user on the same machine could read the file with a plain `open()` — no elevated privileges required — and extract the refresh token.

### Impact

Local credential theft / privilege escalation on multi-user Linux or macOS hosts running under a permissive umask. The stolen refresh token can be exchanged for fresh access tokens via Garmin's OAuth endpoint, granting ongoing access to the victim's account (health/fitness data, activity history, device management) until the token is revoked.

### Patch

Fixed in **0.3.5** (commit `77a3837`). `dump()` now creates the directory as `0o700` and writes the token file as `0o600` regardless of umask — using `os.open(..., O_CREAT|O_WRONLY|O_TRUNC, 0o600)` with `O_NOFOLLOW` where available, plus a defensive `chmod` that also tightens a pre-existing loose file:

```python
p.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
with contextlib.suppress(OSError):
    p.parent.chmod(0o700)
flags = os.O_WRONLY | os.O_CREAT | os.O_TRUNC
if hasattr(os, "O_NOFOLLOW"):
    flags |= os.O_NOFOLLOW
fd = os.open(p, flags, 0o600)
with os.fdopen(fd, "w", encoding="utf-8") as f:
    f.write(self.dumps())
with contextlib.suppress(OSError):
    p.chmod(0o600)
```

Verified under `umask 022`: directory `0o700`, file `0o600`, no group/other access.

### Workarounds

If you cannot upgrade immediately, restrict the token store manually and keep it owner-only:

```bash
chmod 700 ~/.garminconnect
chmod 600 ~/.garminconnect/garmin_tokens.json
```

### Remediation

1. **Upgrade** to `garminconnect >= 0.3.5`:
   ```bash
   pip install --upgrade garminconnect
   ```
2. **Fix any token file already on disk** — upgrading only tightens permissions
   on the *next* write, so an existing world-readable file stays exposed until
   then:
   ```bash
   chmod 600 ~/.garminconnect/garmin_tokens.json
   # or remove it and log in again to mint a fresh token store
   ```
3. **If the file was exposed on a shared host, treat the refresh token as
   compromised.** Re-authenticate (delete the token store and log in again) so
   a new token is issued; consider the previously stored token potentially
   read by others until rotated.

### Credit

Reported by **EQSTLab** via a private security advisory. garminconnect thanks them for the detailed, responsible disclosure.

## References
- https://github.com/cyberjunky/python-garminconnect/security/advisories/GHSA-wjhr-76vg-2hvc
- https://github.com/cyberjunky/python-garminconnect/commit/77a3837f1f79d486663c9646438e70e8319e1a48
- https://github.com/cyberjunky/python-garminconnect/commit/f74174a5647e1af78eca1f8f3a0aa5dc5a899947
- https://github.com/cyberjunky/python-garminconnect
- https://github.com/cyberjunky/python-garminconnect/releases/tag/0.3.5
