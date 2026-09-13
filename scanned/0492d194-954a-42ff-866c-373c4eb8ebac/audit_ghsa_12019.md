# [C] baserCMS Update Functionality Vulnerable to OS Command Injection

## Summary
Severity: Critical
Advisory: GHSA-m9g7-rgfc-jcm7
CVE: CVE-2026-30877
CWE: CWE-78
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2026-03-31
Source: https://github.com/advisories/GHSA-m9g7-rgfc-jcm7
Type: github-advisory

## Affected
- Packagist: `baserproject/basercms` — affected >=0 <5.2.3

## Details
### Summary
The latest version of baserCMS (basercms-5.2.2) contains an OS command injection vulnerability (CWE-78) in its update functionality.
Due to this issue, an authenticated user with administrator privileges in baserCMS can execute arbitrary OS commands on the server with the privileges of the user account running baserCMS.

### Details
Please refer to the attached materials.
[OSコマンドインジェクション（baserCMSのアップデート機能）.pdf](https://github.com/user-attachments/files/25468689/OS.baserCMS.pdf)



### Impact
An authenticated user with administrator privileges in baserCMS can execute OS commands on the server with the privileges of the user account running baserCMS.

## References
- https://github.com/baserproject/basercms/security/advisories/GHSA-m9g7-rgfc-jcm7
- https://nvd.nist.gov/vuln/detail/CVE-2026-30877
- https://basercms.net/security/JVN_20837860
- https://github.com/baserproject/basercms
- https://github.com/baserproject/basercms/releases/tag/5.2.3
