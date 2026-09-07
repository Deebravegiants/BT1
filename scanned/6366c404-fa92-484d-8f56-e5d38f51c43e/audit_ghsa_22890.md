# [C] CodeIgniter Session Fixation Vulnerability

## Summary
Severity: Critical
Advisory: GHSA-g434-3q2j-hj4r
CVE: CVE-2018-12071
CWE: CWE-384
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-g434-3q2j-hj4r
Type: github-advisory

## Affected
- Packagist: `codeigniter/framework` — affected >=0 <3.1.10

## Details
A Session Fixation issue exists in CodeIgniter before 3.1.10 because `session.use_strict_mode` in the Session Library was mishandled.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-12071
- https://github.com/bcit-ci/CodeIgniter/issues/5958
- https://github.com/bcit-ci/CodeIgniter/commit/800a20d6c4662d99ae0988b2f8f2238bb8bb29db
- https://github.com/bcit-ci/CodeIgniter/commit/a9da3dd2f16a8f97d7bc4ff5572b28e4bb84c813#diff-32788a4d3748e8818044886ab43241179c7f5f5b82e979e73146669ca6e2da1cR306
- https://github.com/bcit-ci/CodeIgniter
- https://web.archive.org/web/20181115214804/https://www.codeigniter.com/user_guide/changelog.html#version-3-1-9
- https://www.codeigniter.com/user_guide/changelog.html
