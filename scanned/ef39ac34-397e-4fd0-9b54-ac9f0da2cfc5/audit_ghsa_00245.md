# [C] Koji hub call does not perform correct access checks

## Summary
Severity: Critical
Advisory: GHSA-6mww-xvh7-fq4f
CVE: CVE-2018-1002150
CWE: CWE-732
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2018-07-12
Source: https://github.com/advisories/GHSA-6mww-xvh7-fq4f
Type: github-advisory

## Affected
- PyPI: `koji` — affected >=1.15 <1.15.1
- PyPI: `koji` — affected >=1.14 <1.14.1
- PyPI: `koji` — affected >=1.13 <1.13.1
- PyPI: `koji` — affected >=1.12 <1.12.1

## Details
Koji version 1.12, 1.13, 1.14 and 1.15 contain an incorrect access control vulnerability resulting in arbitrary filesystem read/write access. This vulnerability has been fixed in versions 1.12.1, 1.13.1, 1.14.1 and 1.15.1.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-1002150
- https://docs.pagure.org/koji/CVE-2018-1002150
- https://github.com/advisories/GHSA-6mww-xvh7-fq4f
- https://github.com/pypa/advisory-database/tree/main/vulns/koji/PYSEC-2018-86.yaml
- https://pagure.io/koji
- https://pagure.io/koji/c/ab1ade7
- https://pagure.io/koji/issue/850
