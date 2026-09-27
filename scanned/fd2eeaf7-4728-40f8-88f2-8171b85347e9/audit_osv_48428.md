# [H] CVE-2017-7645

## Summary
Severity: High
Advisory: CVE-2017-7645
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-04-18
Source: https://osv.dev/vulnerability/CVE-2017-7645
Type: osv

## Details
The NFSv2/NFSv3 server in the nfsd subsystem in the Linux kernel through 4.10.11 allows remote attackers to cause a denial of service (system crash) via a long RPC reply, related to net/sunrpc/svc.c, fs/nfsd/nfs3xdr.c, and fs/nfsd/nfsxdr.c.

## References
- http://www.debian.org/security/2017/dsa-3886
- http://www.securityfocus.com/bid/97950
- https://access.redhat.com/errata/RHSA-2017:1616
- https://access.redhat.com/errata/RHSA-2018:1319
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=e6838a29ecb484c97e4efef9429643b9851fba6e
- https://usn.ubuntu.com/3754-1/
- https://access.redhat.com/errata/RHSA-2017:1615
- https://access.redhat.com/errata/RHSA-2017:1647
- https://help.ecostruxureit.com/display/public/UADCE725/Security+fixes+in+StruxureWare+Data+Center+Expert+v7.6.0
- https://marc.info/?l=linux-nfs&m=149247516212924&w=2
- https://marc.info/?l=linux-nfs&m=149218228327497&w=2
- https://github.com/torvalds/linux/commit/e6838a29ecb484c97e4efef9429643b9851fba6e
