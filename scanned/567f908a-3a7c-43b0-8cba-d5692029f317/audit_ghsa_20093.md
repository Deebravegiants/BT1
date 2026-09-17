# [H] rdiffweb has no rate limit on resend email feature

## Summary
Severity: High
Advisory: GHSA-7q4r-x5qg-mmcp
CVE: CVE-2022-4723
CWE: CWE-770
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-12-27
Source: https://github.com/advisories/GHSA-7q4r-x5qg-mmcp
Type: github-advisory

## Affected
- PyPI: `rdiffweb` — affected >=0 <2.5.5

## Details
rdiffweb prior to 2.5.5 has no rate limit on the "resend email feature" while enable or disable 2FA from `/prefs/mfa` endpoint .

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-4723
- https://github.com/ikus060/rdiffweb/commit/6e9ee210548f6d3210704cac302cfc7cdb239765
- https://github.com/ikus060/rdiffweb
- https://github.com/pypa/advisory-database/tree/main/vulns/rdiffweb/PYSEC-2022-43009.yaml
- https://huntr.dev/bounties/9369681b-8bfc-4146-a54c-c5108442d92c
