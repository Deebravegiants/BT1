# [H] CVE-2016-2853

## Summary
Severity: High
Advisory: CVE-2016-2853
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2016-05-02
Source: https://osv.dev/vulnerability/CVE-2016-2853
Type: osv

## Details
The aufs module for the Linux kernel 3.x and 4.x does not properly restrict the mount namespace, which allows local users to gain privileges by mounting an aufs filesystem on top of a FUSE filesystem, and then executing a crafted setuid program.

## References
- http://www.securityfocus.com/bid/96839
- http://www.openwall.com/lists/oss-security/2021/10/18/1
- https://sourceforge.net/p/aufs/mailman/message/34864744/
- http://www.halfdog.net/Security/2016/AufsPrivilegeEscalationInUserNamespaces/
- http://www.openwall.com/lists/oss-security/2016/02/24/9
