# [M] CVE-2019-12379

## Summary
Severity: Medium
Advisory: CVE-2019-12379
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-05-28
Source: https://osv.dev/vulnerability/CVE-2019-12379
Type: osv

## Details
An issue was discovered in con_insert_unipair in drivers/tty/vt/consolemap.c in the Linux kernel through 5.1.5. There is a memory leak in a certain case of an ENOMEM outcome of kmalloc. NOTE: This id is disputed as not being an issue

## References
- https://git.kernel.org/pub/scm/linux/kernel/git/gregkh/tty.git/commit/?h=tty-testing&id=15b3cd8ef46ad1b100e0d3c7e38774f330726820
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/J36BIJTKEPUOZKJNHQBUZA47RQONUKOI/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/KLGWJKLMTBBB53D5QLS4HOY2EH246WBE/
- https://security.netapp.com/advisory/ntap-20190710-0002/
- http://www.securityfocus.com/bid/108478
- https://git.kernel.org/pub/scm/linux/kernel/git/gregkh/tty.git/commit/?h=tty-next&id=84ecc2f6eb1cb12e6d44818f94fa49b50f06e6ac
