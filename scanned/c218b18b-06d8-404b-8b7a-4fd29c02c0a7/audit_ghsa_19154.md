# [H] vxe-table prototype pollution

## Summary
Severity: High
Advisory: GHSA-89fp-f5mx-748x
CVE: CVE-2024-57080
CWE: CWE-1321
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2025-02-06
Source: https://github.com/advisories/GHSA-89fp-f5mx-748x
Type: github-advisory

## Affected
- npm: `vxe-table` — affected >=0

## Details
A prototype pollution in the lib.install function of vxe-table v4.8.10 allows attackers to cause a Denial of Service (DoS) via supplying a crafted payload.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-57080
- https://gist.github.com/tariqhawis/c0b5fa2d7e4edd3f000e73fb7a10ccbc
- https://github.com/x-extends/vxe-table
