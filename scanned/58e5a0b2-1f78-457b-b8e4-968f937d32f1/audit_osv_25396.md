# [H] CVE-2023-35844

## Summary
Severity: High
Advisory: CVE-2023-35844
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2023-06-19
Source: https://osv.dev/vulnerability/CVE-2023-35844
Type: osv

## Details
packages/backend/src/routers in Lightdash before 0.510.3 has insecure file endpoints, e.g., they allow .. directory traversal and do not ensure that an intended file extension (.csv or .png) is used.

## References
- https://github.com/lightdash/lightdash/compare/0.510.2...0.510.3
- https://advisory.dw1.io/59
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/35xxx/CVE-2023-35844.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-35844
- https://github.com/lightdash/lightdash/commit/fcc808c84c2cc3afb343063e32a49440d32a553c
- https://github.com/lightdash/lightdash/pull/5090
