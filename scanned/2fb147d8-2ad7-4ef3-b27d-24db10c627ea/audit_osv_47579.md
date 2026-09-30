# [M] CVE-2016-8646

## Summary
Severity: Medium
Advisory: CVE-2016-8646
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2016-11-28
Source: https://osv.dev/vulnerability/CVE-2016-8646
Type: osv

## Details
The hash_accept function in crypto/algif_hash.c in the Linux kernel before 4.3.6 allows local users to cause a denial of service (OOPS) by attempting to trigger use of in-kernel hash algorithms for a socket that has received zero bytes of data.

## References
- http://www.securityfocus.com/bid/94309
- http://www.openwall.com/lists/oss-security/2016/11/15/2
- https://access.redhat.com/errata/RHSA-2017:1297
- http://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.3.6
- https://access.redhat.com/errata/RHSA-2017:1298
- https://access.redhat.com/errata/RHSA-2017:1308
- https://bugzilla.redhat.com/show_bug.cgi?id=1388821
- https://github.com/torvalds/linux/commit/4afa5f9617927453ac04b24b584f6c718dfb4f45
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=4afa5f9617927453ac04b24b584f6c718dfb4f45
