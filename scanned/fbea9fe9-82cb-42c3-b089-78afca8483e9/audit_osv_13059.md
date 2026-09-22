# [H] CVE-2018-17182

## Summary
Severity: High
Advisory: CVE-2018-17182
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-09-19
Source: https://osv.dev/vulnerability/CVE-2018-17182
Type: osv

## Details
An issue was discovered in the Linux kernel through 4.18.8. The vmacache_flush_all function in mm/vmacache.c mishandles sequence number overflows. An attacker can trigger a use-after-free (and possibly gain privileges) via certain thread creation, map, unmap, invalidation, and dereference operations.

## References
- http://www.securityfocus.com/bid/106503
- https://usn.ubuntu.com/3777-3/
- https://access.redhat.com/errata/RHSA-2018:3656
- https://lists.debian.org/debian-lts-announce/2018/10/msg00003.html
- https://usn.ubuntu.com/3776-1/
- https://www.openwall.com/lists/oss-security/2018/09/18/4
- https://usn.ubuntu.com/3777-2/
- https://usn.ubuntu.com/3776-2/
- https://usn.ubuntu.com/3777-1/
- https://www.debian.org/security/2018/dsa-4308
- http://www.securityfocus.com/bid/105417
- https://github.com/torvalds/linux/commit/7a9cdebdcc17e426fb5287e4a82db1dfe86339b2
- https://security.netapp.com/advisory/ntap-20190204-0001/
- http://www.securitytracker.com/id/1041748
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=7a9cdebdcc17e426fb5287e4a82db1dfe86339b2
- https://www.exploit-db.com/exploits/45497/
