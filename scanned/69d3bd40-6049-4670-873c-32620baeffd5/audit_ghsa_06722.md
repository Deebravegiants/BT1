# [H] Thumbor has path traversal via post-validation URL decoding bypass in file_loader

## Summary
Severity: High
Advisory: GHSA-cj54-hpcc-gj6h
CVE: CVE-2026-53502
CWE: CWE-22
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-07-31
Source: https://github.com/advisories/GHSA-cj54-hpcc-gj6h
Type: github-advisory

## Affected
- PyPI: `thumbor` — affected >=0 <7.8.0

## Details
The file_loader performs `unquote()` on the file path AFTER the `abspath() + startswith()` security check. An attacker can use percent-encoded path traversal sequences (`%2e%2e` for `..`) that pass the security check as literal directory names, but are then decoded to actual `..` traversal sequences.

## Affected code

`thumbor/loaders/file_loader.py` lines 28-49:
```python
async def load(context, path):
    file_path = join(
        context.config.FILE_LOADER_ROOT_PATH.rstrip("/"), path.lstrip("/")
    )
    file_path = abspath(file_path)
    inside_root_path = file_path.startswith(         # Security check
        abspath(context.config.FILE_LOADER_ROOT_PATH)
    )
    result = LoaderResult()
    if not inside_root_path:
        result.error = LoaderResult.ERROR_NOT_FOUND
        result.successful = False
        return result

    if not exists(file_path):
        file_path = unquote(file_path)               # unquote AFTER check!

    if exists(file_path) and isfile(file_path):
        with open(file_path, "rb") as source_file:
            ...
```

The watermark and frame filters pass their URL parameters directly to the loader without re-encoding (unlike the main image URL flow which applies `quote()` in `imaging.py` line 37).

## PoC

```bash
# Read /etc/passwd via watermark filter path traversal
# %252e is double-encoded: Tornado decodes to %2e, filter passes to file_loader,
# file_loader unquote decodes %2e to .
curl 'http://thumbor-host:8888/unsafe/filters:watermark(%252e%252e/%252e%252e/%252e%252e/%252e%252e/etc/passwd,0,0,100)/some-valid-image.jpg'
```

Flow:
1. `%252e%252e` arrives at Tornado, decoded to `%2e%2e`
2. Watermark filter passes `%2e%2e/%2e%2e/.../etc/passwd` to file_loader
3. `join(ROOT, '%2e%2e/...')` = `ROOT/%2e%2e/...`
4. `abspath()` sees `%2e%2e` as literal dir name (no dots to resolve)
5. `startswith(ROOT)` = True (passes check)
6. `exists()` returns False (literal `%2e%2e` dir doesn't exist)
7. `unquote()` converts `%2e%2e` to `..`
8. OS resolves `..` → reads files outside ROOT

## Prerequisites

- `LOADER = thumbor.loaders.file_loader` (or `file_loader_http_fallback`)
- `ALLOW_UNSAFE_URL = True` (this is the default)
- watermark/frame filters are enabled by default (in BUILTIN_FILTERS)

## Impact

Arbitrary file read on the thumbor server. When the file is a valid image format, its content is returned in the response overlaid as a watermark. Can be used to read configuration files, secrets, private keys, etc.

## References
- https://github.com/thumbor/thumbor/security/advisories/GHSA-cj54-hpcc-gj6h
- https://github.com/thumbor/thumbor/commit/3b986d13677b30fe6651c8c72ebb25957ac0a40d
- https://github.com/thumbor/thumbor
- https://github.com/thumbor/thumbor/releases/tag/7.8.0
