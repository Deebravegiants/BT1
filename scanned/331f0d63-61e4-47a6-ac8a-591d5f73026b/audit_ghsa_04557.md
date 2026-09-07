# [H] Docling: Unsafe URI and Path Handling in HTML Backend

## Summary
Severity: High
Advisory: GHSA-q29v-xc37-wh5m
CVE: CVE-2026-47214
CWE: CWE-400, CWE-73
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:L (CVSS_V3)
Published: 2026-06-03
Source: https://github.com/advisories/GHSA-q29v-xc37-wh5m
Type: github-advisory

## Affected
- PyPI: `docling` — affected >=0 <2.94.0

## Details
### Impact
The HTML backend did not perform sufficient validation during resource handling:
- Accepted `file://` URIs enabling local file system access when `enable_local_fetch=True`
- Path resolution allowed traversal outside intended directories via `../` sequences and absolute paths
- Did not block internal network resources under `enable_remote_fetch=True`
- HTTP redirects were not validated, potentially redirecting to unintended schemes
- No resource limits for remote image downloads and `data:` URIs

### Patches
Fixed in versions 2.91.0 (initial fixes) and 2.94.0 (additional improvements). The fixes implement:
- Updated local path treatment: absolute files always blocked, relative paths require `enable_local_fetch=True` (default: False) and containment within configured `base_path` for path traversal protection
- `file://` scheme stripped & treated as local path (above)
- IP address validation to prevent SSRF
- HTTP redirect validation, connection and read timeouts
- Size limit for both remote images (with streaming download) and base64-decoded data URIs

### Workarounds
Keep both `enable_local_fetch=False` and `enable_remote_fetch=False` (defaults) when processing untrusted HTML documents.

### References
- Initial fixes: [v2.91.0](https://github.com/docling-project/docling/releases/tag/v2.91.0)
- Additional improvements: [v2.94.0](https://github.com/docling-project/docling/releases/tag/v2.94.0)

## References
- https://github.com/docling-project/docling/security/advisories/GHSA-q29v-xc37-wh5m
- https://nvd.nist.gov/vuln/detail/CVE-2026-47214
- https://github.com/docling-project/docling
- https://github.com/docling-project/docling/releases/tag/v2.91.0
- https://github.com/docling-project/docling/releases/tag/v2.94.0
- https://github.com/pypa/advisory-database/tree/main/vulns/docling/PYSEC-2026-2146.yaml
