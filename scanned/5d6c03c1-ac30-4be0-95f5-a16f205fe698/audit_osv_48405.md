# [M] CVE-2017-7472

## Summary
Severity: Medium
Advisory: CVE-2017-7472
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-05-11
Source: https://osv.dev/vulnerability/CVE-2017-7472
Type: osv

## Details
The KEYS subsystem in the Linux kernel before 4.10.13 allows local users to cause a denial of service (memory consumption) via a series of KEY_REQKEY_DEFL_THREAD_KEYRING keyctl_set_reqkey_keyring calls.

## References
- http://lists.opensuse.org/opensuse-security-announce/2018-01/msg00007.html
- http://www.securityfocus.com/bid/98422
- https://lkml.org/lkml/2017/4/1/235
- https://lkml.org/lkml/2017/4/3/724
- http://www.securitytracker.com/id/1038471
- https://www.exploit-db.com/exploits/42136/
- https://access.redhat.com/errata/RHSA-2018:0152
- https://access.redhat.com/errata/RHSA-2018:0151
- https://access.redhat.com/errata/RHSA-2018:0181
- https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.10.13
- http://openwall.com/lists/oss-security/2017/05/11/1
- https://bugzilla.redhat.com/show_bug.cgi?id=1442086
- https://github.com/torvalds/linux/commit/c9f838d104fed6f2f61d68164712e3204bf5271b
- https://bugzilla.novell.com/show_bug.cgi?id=1034862
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=c9f838d104fed6f2f61d68164712e3204bf5271b
