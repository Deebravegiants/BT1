# [M] Moodle uses the same key for QR login and auto-login

## Summary
Severity: Medium
Advisory: GHSA-r82w-3phg-qvr4
CVE: CVE-2024-38277
CWE: CWE-324, CWE-326
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2024-06-18
Source: https://github.com/advisories/GHSA-r82w-3phg-qvr4
Type: github-advisory

## Affected
- Packagist: `moodle/moodle` — affected >=4.4.0-beta <4.4.1
- Packagist: `moodle/moodle` — affected >=4.3.0-beta <4.3.5
- Packagist: `moodle/moodle` — affected >=4.2.0-beta <4.2.8
- Packagist: `moodle/moodle` — affected >=0 <4.1.11

## Details
A unique key should be generated for a user's QR login key and their auto-login key, so the same key cannot be used interchangeably between the two.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-38277
- https://github.com/moodle/moodle/commit/0caedaab7cd5a46331d56654ce9301b0a5a04c56
- https://github.com/moodle/moodle/commit/1aea4a15281d81f2414a95aa485b8a6551708f57
- https://github.com/moodle/moodle/commit/ad46a97f5355f0451d52e9f1a0f528d9a6f12e06
- https://github.com/moodle/moodle/commit/d05795db8eece2943241a29a5443fb4685ba6070
- https://github.com/moodle/moodle
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/F7AZYR7EXV6E5SQE2GYTNQE3NOENJCQ6
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/GHTIX55J4Q4LEOMLNEA4OZSWVEENQX7E
- https://moodle.org/mod/forum/discuss.php?d=459502
