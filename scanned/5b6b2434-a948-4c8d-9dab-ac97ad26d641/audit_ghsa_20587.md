# [H] dnslib has DNS reply verification issue

## Summary
Severity: High
Advisory: GHSA-r478-c2pc-m7gx
CVE: CVE-2022-22846
CWE: CWE-345
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-01-12
Source: https://github.com/advisories/GHSA-r478-c2pc-m7gx
Type: github-advisory

## Affected
- PyPI: `dnslib` — affected >=0 <0.9.17

## Details
The dnslib package through 0.9.16 for Python does not verify that the ID value in a DNS reply matches an ID value in a query.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-22846
- https://github.com/paulc/dnslib/issues/30
- https://github.com/paulc/dnslib/commit/76e8677699ed098387d502c57980f58da642aeba
- https://github.com/advisories/GHSA-r478-c2pc-m7gx
- https://github.com/paulc/dnslib
- https://github.com/pypa/advisory-database/tree/main/vulns/dnslib/PYSEC-2022-4.yaml
