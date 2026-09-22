# [H] privacyIDEA Improper Input Validation vulnerability

## Summary
Severity: High
Advisory: GHSA-7qqv-r2q4-jxhm
CVE: CVE-2018-1000809
CWE: CWE-20
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2019-01-14
Source: https://github.com/advisories/GHSA-7qqv-r2q4-jxhm
Type: github-advisory

## Affected
- PyPI: `privacyIDEA` — affected >=0 <2.23.2

## Details
privacyIDEA version 2.23.1 and earlier contains a Improper Input Validation vulnerability in token validation api that can result in Denial-of-Service. This attack appear to be exploitable via http request with user=<space>&pass= to /validate/check url. This vulnerability appears to have been fixed in 2.23.2.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-1000809
- https://github.com/privacyidea/privacyidea/issues/1227
- https://github.com/privacyidea/privacyidea/commit/a3edc09beffa2104f357fe24971ea3211ce40751
- https://github.com/advisories/GHSA-7qqv-r2q4-jxhm
- https://github.com/privacyidea/privacyidea
- https://github.com/pypa/advisory-database/tree/main/vulns/privacyidea/PYSEC-2018-20.yaml
