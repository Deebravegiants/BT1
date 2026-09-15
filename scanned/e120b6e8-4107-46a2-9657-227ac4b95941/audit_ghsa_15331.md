# [M] In aiohttp, compressed files as symlinks are not protected from path traversal

## Summary
Severity: Medium
Advisory: GHSA-jwhx-xcg6-8xhj
CVE: CVE-2024-42367
CWE: CWE-61
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2024-08-09
Source: https://github.com/advisories/GHSA-jwhx-xcg6-8xhj
Type: github-advisory

## Affected
- PyPI: `aiohttp` — affected >=3.10.0b1 <3.10.2

## Details
### Summary
Static routes which contain files with compressed variants (`.gz` or `.br` extension) were vulnerable to path traversal outside the root directory if those variants are symbolic links.

### Details
The server protects static routes from path traversal outside the root directory when `follow_symlinks=False` (default).  It does this by resolving the requested URL to an absolute path and then checking that path relative to the root.  However, these checks are not performed when looking for compressed variants in the `FileResponse` class, and symbolic links are then automatically followed when performing `Path.stat()` and `Path.open()` to send the file.

### Impact
Servers with static routes that contain compressed variants as symbolic links, pointing outside the root directory, or that permit users to upload or create such links, are impacted.

----

Patch: https://github.com/aio-libs/aiohttp/pull/8653/files

## References
- https://github.com/aio-libs/aiohttp/security/advisories/GHSA-jwhx-xcg6-8xhj
- https://nvd.nist.gov/vuln/detail/CVE-2024-42367
- https://github.com/aio-libs/aiohttp/pull/8653
- https://github.com/aio-libs/aiohttp/commit/ce2e9758814527589b10759a20783fb03b98339f
- https://github.com/aio-libs/aiohttp
- https://github.com/aio-libs/aiohttp/blob/e0ff5246e1d29b7710ab1a2bbc972b48169f1c05/aiohttp/web_fileresponse.py#L177
- https://github.com/aio-libs/aiohttp/blob/e0ff5246e1d29b7710ab1a2bbc972b48169f1c05/aiohttp/web_urldispatcher.py#L674
