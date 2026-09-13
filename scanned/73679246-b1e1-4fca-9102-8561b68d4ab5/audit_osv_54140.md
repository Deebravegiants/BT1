# [H] CVE-2023-4004

## Summary
Severity: High
Advisory: CVE-2023-4004
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-07-31
Source: https://osv.dev/vulnerability/CVE-2023-4004
Type: osv

## Details
A use-after-free flaw was found in the Linux kernel's netfilter in the way a user triggers the nft_pipapo_remove function with the element, without a NFT_SET_EXT_KEY_END. This issue could allow a local user to crash the system or potentially escalate their privileges on the system.

## References
- http://packetstormsecurity.com/files/175072/Kernel-Live-Patch-Security-Notice-LSN-0098-1.html
- https://lists.debian.org/debian-lts-announce/2023/10/msg00027.html
- http://packetstormsecurity.com/files/175963/Kernel-Live-Patch-Security-Notice-LSN-0099-1.html
- https://access.redhat.com/errata/RHSA-2023:5221
- https://security.netapp.com/advisory/ntap-20231027-0001/
- https://access.redhat.com/errata/RHSA-2023:5244
- https://access.redhat.com/errata/RHSA-2023:7382
- https://access.redhat.com/errata/RHSA-2023:7411
- https://www.debian.org/security/2023/dsa-5480
- https://access.redhat.com/errata/RHSA-2023:4961
- https://access.redhat.com/errata/RHSA-2023:4967
- https://access.redhat.com/errata/RHSA-2023:5091
- https://access.redhat.com/errata/RHSA-2023:5548
- https://access.redhat.com/security/cve/CVE-2023-4004
- https://access.redhat.com/errata/RHSA-2023:5255
- https://access.redhat.com/errata/RHSA-2023:5627
- https://access.redhat.com/errata/RHSA-2023:7389
- https://access.redhat.com/errata/RHSA-2023:7417
- https://access.redhat.com/errata/RHSA-2023:7431
- https://access.redhat.com/errata/RHSA-2023:7434
