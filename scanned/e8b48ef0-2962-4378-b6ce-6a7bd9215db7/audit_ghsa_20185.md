# [M] Access control issue in AlekSIS-Core

## Summary
Severity: Medium
Advisory: GHSA-76x2-h8h3-cwjg
CVE: CVE-2022-29773
CWE: CWE-863
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-06-04
Source: https://github.com/advisories/GHSA-76x2-h8h3-cwjg
Type: github-advisory

## Affected
- PyPI: `aleksis-core` — affected >=0 <2.9

## Details
An access control issue in aleksis/core/util/auth_helpers.py: ClientProtectedResourceMixin of AlekSIS-Core v2.8.1 and below allows attackers to access arbitrary scopes if no allowed scopes are specifically set.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-29773
- https://aleksis.org/2022-05-04_advisory.html
- https://edugit.org/AlekSIS/official/AlekSIS-Core
- https://edugit.org/AlekSIS/official/AlekSIS-Core/-/commit/0d39d5f566e1d916e3c8dedd3f5bd62161f30bd8
- https://edugit.org/AlekSIS/official/AlekSIS-Core/-/issues/688
- https://edugit.org/AlekSIS/official/AlekSIS-Core/-/merge_requests/1011
