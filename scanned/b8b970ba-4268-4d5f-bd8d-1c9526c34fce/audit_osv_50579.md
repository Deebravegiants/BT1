# [H] CVE-2020-24331

## Summary
Severity: High
Advisory: CVE-2020-24331
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-08-13
Source: https://osv.dev/vulnerability/CVE-2020-24331
Type: osv

## Details
An issue was discovered in TrouSerS through 0.3.14. If the tcsd daemon is started with root privileges, the tss user still has read and write access to the /etc/tcsd.conf file (which contains various settings related to this daemon).

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/SSDL7COIFCZQMUBNAASNMKMX7W5JUHRD/
- https://bugzilla.suse.com/show_bug.cgi?id=1164472
- https://seclists.org/oss-sec/2020/q2/att-135/tcsd_fixes.patch
- https://sourceforge.net/p/trousers/mailman/message/37015817/
- http://www.openwall.com/lists/oss-security/2020/08/14/1
