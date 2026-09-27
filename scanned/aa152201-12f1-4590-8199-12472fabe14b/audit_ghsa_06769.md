# [H] Thumbor treats ALLOWED_SOURCES string patterns as unescaped regex, allowing hostname bypass via wildcard dot

## Summary
Severity: High
Advisory: GHSA-6x26-6r6f-m537
CVE: CVE-2026-53500
CWE: CWE-1333
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:L (CVSS_V3)
Published: 2026-07-31
Source: https://github.com/advisories/GHSA-6x26-6r6f-m537
Type: github-advisory

## Affected
- PyPI: `thumbor` — affected >=0 <7.8.0

## Details
## Summary

The `ALLOWED_SOURCES` configuration is meant to restrict which hosts Thumbor's HTTP loader may fetch images from. Plain-string entries in that list (the overwhelming majority of real-world and documented configurations) are passed directly to `re.match()` without escaping. Because `.` is a regex wildcard, every dot in a domain name becomes a bypass vector: `s.glbimg.com` silently matches `sXglbimgYcom`, `sAglbimg.com`, and any other hostname that differs only at a dot position. This undermines the primary SSRF defence that `ALLOWED_SOURCES` is intended to provide.

## Affected component

`thumbor/loaders/http_loader.py` — `validate()`

## Proof of concept

```python
import re
from thumbor.config import Config
from thumbor.context import Context
from thumbor.loaders import http_loader as loader

config = Config()
config.ALLOWED_SOURCES = ["s.glbimg.com"]   # typical user config
ctx = Context(None, config, None)

# These should be blocked — both return True due to the unescaped dot
print(loader.validate(ctx, "http://sXglbimgYcom/secret.jpg"))  # True ← bypass
print(loader.validate(ctx, "http://sAglbimg.com/secret.jpg"))  # True ← bypass

# Legitimate origin — correctly allowed
print(loader.validate(ctx, "http://s.glbimg.com/logo.jpg"))    # True ← correct
```

## Root cause

`thumbor/loaders/http_loader.py` (before fix):

```python
for pattern in context.config.ALLOWED_SOURCES:
    if isinstance(pattern, Pattern):
        match = url
    else:
        pattern = f"^{pattern}$"   # <-- dots not escaped, act as regex wildcard
        match = res.hostname

    if re.match(pattern, match):
        return True
```

## Impact

An attacker who can influence the image source URL passed to Thumbor can fetch images from arbitrary hosts, bypassing the `ALLOWED_SOURCES` allowlist.

**Preconditions:**

- `ALLOWED_SOURCES` contains at least one plain-string entry (the common case; all official documentation examples use plain strings).
- The attacker can supply or influence the image URL — true whenever  `ALLOW_UNSAFE_URL = True` (the default), or when the application forwards user input to a signed URL endpoint.

## Fix

Apply `re.escape()` to plain-string patterns before compiling them, so every
character is matched literally:

```python
else:
    pattern = f"^{re.escape(pattern)}$"   # dots and other metacharacters are now literal
    match = res.hostname
```

This is a one-call addition with no breaking change for correctly written configurations. Users who need real regular-expression behaviour should supply a compiled pattern (`re.compile(r"s\.glbimg\.com")`), which is already handled by the existing `isinstance(pattern, Pattern)` branch and is unaffected by this change.

The `ALLOWED_SOURCES` docstring in `config.py` was also updated to document the two-mode behaviour explicitly.

## References
- https://github.com/thumbor/thumbor/security/advisories/GHSA-6x26-6r6f-m537
- https://github.com/thumbor/thumbor/commit/68876715350c6c8f49c324e5515e64908830aed7
- https://github.com/thumbor/thumbor
- https://github.com/thumbor/thumbor/releases/tag/7.8.0
