# [H] CVE-2024-27442

## Summary
Severity: High
Advisory: CVE-2024-27442
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-08-12
Source: https://osv.dev/vulnerability/CVE-2024-27442
Type: osv

## Details
An issue was discovered in Zimbra Collaboration (ZCS) 9.0 and 10.0. The zmmailboxdmgr binary, a component of ZCS, is intended to be executed by the zimbra user with root privileges for specific mailbox operations. However, an attacker can escalate privileges from the zimbra user to root, because of improper handling of input arguments. An attacker can execute arbitrary commands with elevated privileges, leading to local privilege escalation.

## References
- https://wiki.zimbra.com/wiki/Zimbra_Releases/10.0.7#Security_Fixes
- https://wiki.zimbra.com/wiki/Zimbra_Releases/9.0.0/P39#Security_Fixes
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/27xxx/CVE-2024-27442.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-27442
