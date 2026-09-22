# [M] rdiffweb allows a new password to be the same as the previous password

## Summary
Severity: Medium
Advisory: GHSA-7wr6-fj4x-893v
CVE: CVE-2022-3376
CWE: CWE-521
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2022-10-06
Source: https://github.com/advisories/GHSA-7wr6-fj4x-893v
Type: github-advisory

## Affected
- PyPI: `rdiffweb` — affected >=0 <2.5.0

## Details
rdiffweb prior to 2.5.0a4 allows users to set their new password to be the same as the old password during a password reset. Version 2.5.0a4 enforces a password policy in which a new password cannot be the same as the old one.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-3376
- https://github.com/ikus060/rdiffweb/commit/2ffc2af65c8f8113b06e0b89929c604bcdf844b9
- https://github.com/ikus060/rdiffweb
- https://github.com/pypa/advisory-database/tree/main/vulns/rdiffweb/PYSEC-2022-43157.yaml
- https://huntr.dev/bounties/a9021e93-6d18-4ac1-98ce-550c4697a4ed
