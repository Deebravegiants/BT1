# [C] baserCMS File Uploader Remote Code Execution (RCE) vulnerability

## Summary
Severity: Critical
Advisory: GHSA-h4cc-fxpp-pgw9
CVE: CVE-2023-25654
CWE: CWE-434
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-03-23
Source: https://github.com/advisories/GHSA-h4cc-fxpp-pgw9
Type: github-advisory

## Affected
- Packagist: `baserproject/basercms` — affected >=0 <4.7.5

## Details
### Impact
There is a Remote Code Execution (RCE) Vulnerability on the management system of baserCMS.

### Target
baserCMS 4.7.3 and earlier versions

### Patches
Update to the latest version of baserCMS

### Credits
島峰泰平＠三井物産セキュアディレクション株式会社

## References
- https://github.com/baserproject/basercms/security/advisories/GHSA-h4cc-fxpp-pgw9
- https://nvd.nist.gov/vuln/detail/CVE-2023-25654
- https://github.com/baserproject/basercms/commit/002886be0998c74c386e04f0b43688a8a45d7a96
- https://github.com/baserproject/basercms/commit/08247f0a633d8e836ce2e5cd2d53aa19901a1359
- https://github.com/baserproject/basercms/commit/60f83054d8131b0ace60716cec7e629b5eb3a8f0
- https://github.com/baserproject/basercms
- https://github.com/baserproject/basercms/releases/tag/basercms-4.7.5
