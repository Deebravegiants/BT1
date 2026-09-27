# [C] baserCMS allows any file to be uploaded

## Summary
Severity: Critical
Advisory: GHSA-mfvg-qwcw-qvc8
CVE: CVE-2023-25655
CWE: CWE-434
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-03-23
Source: https://github.com/advisories/GHSA-mfvg-qwcw-qvc8
Type: github-advisory

## Affected
- Packagist: `baserproject/basercms` — affected >=0 <4.7.5

## Details
There is a vulnerability that allows uploading any files to baserCMS.

This is a vulnerability that needs to be addressed when the management system is used by an unspecified number of users.
If you are eligible, please update to the new version as soon as possible.

### Target
baserCMS 4.7.3 and earlier versions

### Vulnerability
Malicious files may be uploaded in Upload File Management.

### Countermeasures
Update to the latest version of baserCMS

Please refer to the following page to reference for more information.
https://basercms.net/security/JVN_61105618

### Credits
- Taisei Inoue@GMO Cybersecurity by Ierae, Inc.
- Yusuke Akagi@Mitsui Bussan Secure Directions, Inc.

## References
- https://github.com/baserproject/basercms/security/advisories/GHSA-mfvg-qwcw-qvc8
- https://nvd.nist.gov/vuln/detail/CVE-2023-25655
- https://github.com/baserproject/basercms/commit/922025a98b0e697ab78f6a785a004e0729aa9100
- https://github.com/baserproject/basercms/commit/9297629983ed908c7f51bf61a0231dde91404ebd
- https://github.com/baserproject/basercms
- https://github.com/baserproject/basercms/releases/tag/basercms-4.7.5
