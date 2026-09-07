# [M] Moodle BigBlueButton web service leaks meeting joining information

## Summary
Severity: Medium
Advisory: GHSA-x29x-qwvx-fxr2
CVE: CVE-2024-38273
CWE: CWE-284
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2024-06-18
Source: https://github.com/advisories/GHSA-x29x-qwvx-fxr2
Type: github-advisory

## Affected
- Packagist: `moodle/moodle` — affected >=4.4.0-beta <4.4.1
- Packagist: `moodle/moodle` — affected >=4.3.0-beta <4.3.5
- Packagist: `moodle/moodle` — affected >=4.2.0-beta <4.2.8
- Packagist: `moodle/moodle` — affected >=0 <4.1.11

## Details
Insufficient capability checks meant it was possible for users to gain access to BigBlueButton join URLs they did not have permission to access.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-38273
- https://github.com/moodle/moodle/commit/500cec575731fd8575569dcb5811535751dddae1
- https://github.com/moodle/moodle/commit/647b9dc06409211018c9f28581504d096ce9e3a8
- https://github.com/moodle/moodle/commit/6c0645ca29b195b5caaffc27d80f2ff715c33a48
- https://github.com/moodle/moodle/commit/a10506b8d70609478fef156d489e0c7d727b6098
- https://github.com/moodle/moodle
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/F7AZYR7EXV6E5SQE2GYTNQE3NOENJCQ6
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/GHTIX55J4Q4LEOMLNEA4OZSWVEENQX7E
- https://moodle.org/mod/forum/discuss.php?d=459498
