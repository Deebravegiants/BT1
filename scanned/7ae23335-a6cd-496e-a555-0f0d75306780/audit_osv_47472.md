# [H] CVE-2016-6187

## Summary
Severity: High
Advisory: CVE-2016-6187
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2016-08-06
Source: https://osv.dev/vulnerability/CVE-2016-6187
Type: osv

## Details
The apparmor_setprocattr function in security/apparmor/lsm.c in the Linux kernel before 4.6.5 does not validate the buffer size, which allows local users to gain privileges by triggering an AppArmor setprocattr hook.

## References
- http://marc.info/?l=linux-kernel&m=146793642811929&w=2
- http://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.6.5
- http://www.openwall.com/lists/oss-security/2016/07/09/2
- http://www.securityfocus.com/bid/91696
- https://bugzilla.redhat.com/show_bug.cgi?id=1354383
- https://github.com/torvalds/linux/commit/30a46a4647fd1df9cf52e43bf467f0d9265096ca
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=30a46a4647fd1df9cf52e43bf467f0d9265096ca
