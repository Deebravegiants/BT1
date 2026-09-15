# [M] CVE-2020-24332

## Summary
Severity: Medium
Advisory: CVE-2020-24332
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-08-13
Source: https://osv.dev/vulnerability/CVE-2020-24332
Type: osv

## Details
An issue was discovered in TrouSerS through 0.3.14. If the tcsd daemon is started with root privileges, the creation of the system.data file is prone to symlink attacks. The tss user can be used to create or corrupt existing files, which could possibly lead to a DoS attack.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/SSDL7COIFCZQMUBNAASNMKMX7W5JUHRD/
- https://bugzilla.suse.com/show_bug.cgi?id=1164472
- https://seclists.org/oss-sec/2020/q2/att-135/tcsd_fixes.patch
- https://sourceforge.net/p/trousers/mailman/message/37015817/
- http://www.openwall.com/lists/oss-security/2020/08/14/1
