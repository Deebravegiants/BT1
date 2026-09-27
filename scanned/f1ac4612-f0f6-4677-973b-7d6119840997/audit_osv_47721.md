# [M] CVE-2017-10911

## Summary
Severity: Medium
Advisory: CVE-2017-10911
CVSS: 6.5 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:N/A:N)
Published: 2017-07-05
Source: https://osv.dev/vulnerability/CVE-2017-10911
Type: osv

## Details
The make_response function in drivers/block/xen-blkback/blkback.c in the Linux kernel before 4.11.8 allows guest OS users to obtain sensitive information from host OS (or other guest OS) kernel memory by leveraging the copying of uninitialized padding fields in Xen block-interface response structures, aka XSA-216.

## References
- https://lists.debian.org/debian-lts-announce/2018/09/msg00007.html
- http://www.debian.org/security/2017/dsa-3945
- https://security.gentoo.org/glsa/201708-03
- http://www.debian.org/security/2017/dsa-3920
- http://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.11.8
- http://www.securityfocus.com/bid/99162
- http://www.securitytracker.com/id/1038720
- https://xenbits.xen.org/xsa/advisory-216.html
- http://www.debian.org/security/2017/dsa-3927
- https://github.com/torvalds/linux/commit/089bc0143f489bd3a4578bdff5f4ca68fb26f341
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=089bc0143f489bd3a4578bdff5f4ca68fb26f341
