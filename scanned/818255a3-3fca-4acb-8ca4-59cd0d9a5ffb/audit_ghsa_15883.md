# [M] Alist reflected Cross-Site Scripting vulnerability

## Summary
Severity: Medium
Advisory: GHSA-8pph-gfhp-w226
CVE: CVE-2024-47067
CWE: CWE-79
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2024-10-10
Source: https://github.com/advisories/GHSA-8pph-gfhp-w226
Type: github-advisory

## Affected
- Go: `github.com/alist-org/alist/v3` — affected >=0 <3.29.0

## Details
AList is a file list program that supports multiple storages. AList contains a reflected cross-site scripting vulnerability in helper.go. The endpoint /i/:link_name takes in a user-provided value and reflects it back in the response. The endpoint returns an application/xml response, opening it up to HTML tags via XHTML and thus leading to a XSS vulnerability. This vulnerability is fixed in 3.29.0.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-47067
- https://github.com/alist-org/alist/commit/6100647310594868e931f3de1188ddd8bde93b78
- https://github.com/alist-org/alist
- https://securitylab.github.com/advisories/GHSL-2023-220_Alist
