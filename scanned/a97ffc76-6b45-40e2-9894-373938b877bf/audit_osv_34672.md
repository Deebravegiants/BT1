# [H] CVE-2025-63656

## Summary
Severity: High
Advisory: CVE-2025-63656
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-01-29
Source: https://osv.dev/vulnerability/CVE-2025-63656
Type: osv

## Details
An out-of-bounds read in the header_cmp function (mk_server/mk_http_parser.c) of monkey commit f37e984 allows attackers to cause a Denial of Service (DoS) via sending a crafted HTTP request to the server.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/63xxx/CVE-2025-63656.json
- https://github.com/archersec/security-advisories/blob/master/monkey/monkey-advisory-2025.md
- https://nvd.nist.gov/vuln/detail/CVE-2025-63656
- https://github.com/monkey/monkey/issues/426
