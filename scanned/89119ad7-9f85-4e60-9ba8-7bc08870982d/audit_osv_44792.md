# [M] nbviewer through 1.0.1 Path Traversal via LocalFileHandler

## Summary
Severity: Medium
Advisory: CVE-2026-86258
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-09-06
Source: https://osv.dev/vulnerability/CVE-2026-86258
Type: osv

## Details
nbviewer through 1.0.1 contains a path traversal vulnerability in LocalFileHandler.can_show() that uses string-prefix comparison instead of proper path validation. Attackers can read files from sibling directories outside the configured root by requesting paths that share the root as a textual prefix, disclosing unintended notebooks and credentials.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/86xxx/CVE-2026-86258.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-86258
- https://www.vulncheck.com/advisories/nbviewer-through-1.0.1-path-traversal-via-localfilehandler
- https://github.com/jupyter/nbviewer/issues/1115
- https://github.com/jupyter/nbviewer/commit/aad36106f72a1ca7721310c6fccc677ce4c744a5
- https://github.com/jupyter/nbviewer
- https://github.com/jupyter/nbviewer/blob/1.0.1/nbviewer/providers/local/handlers.py#L92-L107
