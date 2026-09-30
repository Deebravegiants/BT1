# [M] CVE-2023-3863

## Summary
Severity: Medium
Advisory: CVE-2023-3863
CVSS: 4.1 (CVSS:3.1/AV:L/AC:H/PR:H/UI:N/S:U/C:H/I:N/A:N)
Published: 2023-07-24
Source: https://osv.dev/vulnerability/CVE-2023-3863
Type: osv

## Details
A use-after-free flaw was found in nfc_llcp_find_local in net/nfc/llcp_core.c in NFC in the Linux kernel. This flaw allows a local user with special privileges to impact a kernel information leak issue.

## References
- https://lists.debian.org/debian-lts-announce/2023/10/msg00027.html
- https://security.netapp.com/advisory/ntap-20240202-0002/
- https://www.debian.org/security/2023/dsa-5480
- https://www.debian.org/security/2023/dsa-5492
- https://access.redhat.com/security/cve/CVE-2023-3863
- https://bugzilla.redhat.com/show_bug.cgi?id=2225126
- https://github.com/torvalds/linux/commit/6709d4b7bc2e079241fdef15d1160581c5261c10
