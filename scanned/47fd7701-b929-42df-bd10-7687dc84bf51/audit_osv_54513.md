# [H] CVE-2024-0565

## Summary
Severity: High
Advisory: CVE-2024-0565
CVSS: 7.4 (CVSS:3.1/AV:A/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:H)
Published: 2024-01-15
Source: https://osv.dev/vulnerability/CVE-2024-0565
Type: osv

## Details
An out-of-bounds memory read flaw was found in receive_encrypted_standard in fs/smb/client/smb2ops.c in the SMB Client sub-component in the Linux Kernel. This issue occurs due to integer underflow on the memcpy length, leading to a denial of service.

## References
- https://lists.debian.org/debian-lts-announce/2024/06/msg00017.html
- https://access.redhat.com/errata/RHSA-2024:1188
- https://access.redhat.com/errata/RHSA-2024:1404
- https://access.redhat.com/errata/RHSA-2024:1607
- https://access.redhat.com/errata/RHSA-2024:2093
- https://access.redhat.com/security/cve/CVE-2024-0565
- https://access.redhat.com/errata/RHSA-2024:1532
- https://access.redhat.com/errata/RHSA-2024:1533
- https://access.redhat.com/errata/RHSA-2024:1614
- https://access.redhat.com/errata/RHSA-2024:2394
- https://security.netapp.com/advisory/ntap-20240223-0002/
- https://bugzilla.redhat.com/show_bug.cgi?id=2258518
- https://www.spinics.net/lists/stable-commits/msg328851.html
