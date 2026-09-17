# [H] CVE-2025-46175

## Summary
Severity: High
Advisory: CVE-2025-46175
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2025-11-26
Source: https://osv.dev/vulnerability/CVE-2025-46175
Type: osv

## Details
Ruoyi v4.8.0 is vulnerable to Incorrect Access Control. There is a missing checkUserDataScope permission check in the authRole method of SysUserController.java.

## References
- https://gist.github.com/Han-tj/74d2ed84ede1909da55090fed410d288
- https://gitee.com/y_project/RuoYi/commit/f935b2782f4237cdbcc13bdce76703e82c42f4fe
- https://gitee.com/y_project/RuoYi/issues/IC1FS0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/46xxx/CVE-2025-46175.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-46175
