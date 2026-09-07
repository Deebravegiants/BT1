# [H] Koji blacklisted paths workaround

## Summary
Severity: High
Advisory: GHSA-vwp5-w4rq-g4cc
CVE: CVE-2017-1002153
CWE: CWE-20
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-vwp5-w4rq-g4cc
Type: github-advisory

## Affected
- PyPI: `koji` — affected >=0 <1.15.0

## Details
Koji 1.13.0 does not properly validate SCM paths, allowing an attacker to work around blacklisted paths for build submission.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-1002153
- https://github.com/koji-project/koji
- https://github.com/pypa/advisory-database/tree/main/vulns/koji/PYSEC-2017-144.yaml
- https://pagure.io/koji/issue/563
