# [C] CVE-2017-7895

## Summary
Severity: Critical
Advisory: CVE-2017-7895
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-04-28
Source: https://osv.dev/vulnerability/CVE-2017-7895
Type: osv

## Details
The NFSv2 and NFSv3 server implementations in the Linux kernel through 4.10.13 lack certain checks for the end of a buffer, which allows remote attackers to trigger pointer-arithmetic errors or possibly have unspecified other impact via crafted requests, related to fs/nfsd/nfs3xdr.c and fs/nfsd/nfsxdr.c.

## References
- https://access.redhat.com/errata/RHSA-2017:1616
- https://access.redhat.com/errata/RHSA-2017:2412
- https://access.redhat.com/errata/RHSA-2017:2429
- http://www.debian.org/security/2017/dsa-3886
- http://www.securityfocus.com/bid/98085
- https://access.redhat.com/errata/RHSA-2017:1615
- https://access.redhat.com/errata/RHSA-2017:1766
- https://access.redhat.com/errata/RHSA-2017:1798
- https://access.redhat.com/errata/RHSA-2017:1715
- https://access.redhat.com/errata/RHSA-2017:2472
- https://access.redhat.com/errata/RHSA-2017:2732
- https://access.redhat.com/errata/RHSA-2017:1647
- https://access.redhat.com/errata/RHSA-2017:1723
- https://access.redhat.com/errata/RHSA-2017:2428
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=13bf9fbff0e5e099e2b6f003a0ab8ae145436309
- https://github.com/torvalds/linux/commit/13bf9fbff0e5e099e2b6f003a0ab8ae145436309
