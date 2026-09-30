# [C]  Deserialization of Untrusted Data in codeception/codeception

## Summary
Severity: Critical
Advisory: GHSA-4574-qv3w-fcmg
CVE: CVE-2021-23420
CWE: CWE-502
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-09-01
Source: https://github.com/advisories/GHSA-4574-qv3w-fcmg
Type: github-advisory

## Affected
- Packagist: `codeception/codeception` — affected >=0 <3.1.3
- Packagist: `codeception/codeception` — affected >=4.0.0 <4.1.22

## Details
This affects the package codeception/codeception from 4.0.0 before 4.1.22 and before 3.1.3. The RunProcess class can be leveraged as a gadget to run arbitrary commands on a system that is deserializing user input without validation.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-23420
- https://github.com/Codeception/Codeception/pull/6241
- https://github.com/Codeception/Codeception/commit/802a108057d250ee563120eaa5365a519afc0a71
- https://github.com/Codeception/Codeception/commit/cbce9ea7f4664052fa1ac6b36f5b5a6dbd864d71
- https://github.com/Codeception/Codeception
- https://github.com/Codeception/Codeception/blob/4.1/CHANGELOG-4.x.md#4122
- https://github.com/Codeception/Codeception/blob/4.1/ext/RunProcess.php#L52
- https://github.com/FriendsOfPHP/security-advisories/blob/master/codeception/codeception/CVE-2021-23420.yaml
- https://github.com/JinYiTong/poc
- https://github.com/advisories/GHSA-4574-qv3w-fcmg
- https://snyk.io/vuln/SNYK-PHP-CODECEPTIONCODECEPTION-1324585
