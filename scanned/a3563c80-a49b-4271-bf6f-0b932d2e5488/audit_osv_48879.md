# [H] CVE-2018-16871

## Summary
Severity: High
Advisory: CVE-2018-16871
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-07-30
Source: https://osv.dev/vulnerability/CVE-2018-16871
Type: osv

## Details
A flaw was found in the Linux kernel's NFS implementation, all versions 3.x and all versions 4.x up to 4.20. An attacker, who is able to mount an exported NFS filesystem, is able to trigger a null pointer dereference by using an invalid NFS sequence. This can panic the machine and deny access to the NFS server. Any outstanding disk writes to the NFS server will be lost.

## References
- https://support.f5.com/csp/article/K18657134?utm_source=f5support&amp%3Butm_medium=RSS
- https://access.redhat.com/errata/RHSA-2019:2696
- https://access.redhat.com/errata/RHSA-2019:2730
- https://access.redhat.com/errata/RHSA-2020:0740
- https://security.netapp.com/advisory/ntap-20211004-0002/
- https://support.f5.com/csp/article/K18657134
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2018-16871
