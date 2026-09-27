# [H] CVE-2025-46174

## Summary
Severity: High
Advisory: CVE-2025-46174
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2025-11-26
Source: https://osv.dev/vulnerability/CVE-2025-46174
Type: osv

## Details
Ruoyi v4.8.0 vulnerable to Incorrect Access Control. There is a missing checkUserDataScope permission check in the resetPwd Method of SysUserController.java.

## References
- https://gist.github.com/Han-tj/29543ce0dae8cbb3bcbedca3390844a9
- https://gitee.com/y_project/RuoYi/commit/ea4af7a8cf54393b11d3d286e0aaeb3df8a9aaef
- https://gitee.com/y_project/RuoYi/issues/IC1JZR
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/46xxx/CVE-2025-46174.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-46174
