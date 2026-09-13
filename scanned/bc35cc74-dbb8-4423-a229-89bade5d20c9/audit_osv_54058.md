# [M] CVE-2023-3772

## Summary
Severity: Medium
Advisory: CVE-2023-3772
CVSS: 4.4 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-07-25
Source: https://osv.dev/vulnerability/CVE-2023-3772
Type: osv

## Details
A flaw was found in the Linux kernel’s IP framework for transforming packets (XFRM subsystem). This issue may allow a malicious user with CAP_NET_ADMIN privileges to directly dereference a NULL pointer in xfrm_update_ae_params(), leading to a possible kernel crash and denial of service.

## References
- http://www.openwall.com/lists/oss-security/2023/08/10/3
- https://lists.debian.org/debian-lts-announce/2023/10/msg00027.html
- https://lists.debian.org/debian-lts-announce/2024/01/msg00004.html
- http://www.openwall.com/lists/oss-security/2023/08/10/1
- https://www.debian.org/security/2023/dsa-5492
- https://access.redhat.com/errata/RHSA-2023:6583
- https://access.redhat.com/errata/RHSA-2023:6901
- https://access.redhat.com/errata/RHSA-2023:7077
- https://access.redhat.com/errata/RHSA-2024:0412
- https://access.redhat.com/security/cve/CVE-2023-3772
- https://access.redhat.com/errata/RHSA-2024:0575
- https://bugzilla.redhat.com/show_bug.cgi?id=2218943
