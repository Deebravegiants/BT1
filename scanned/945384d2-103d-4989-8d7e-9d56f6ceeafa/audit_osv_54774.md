# [M] CVE-2024-38796

## Summary
Severity: Medium
Advisory: CVE-2024-38796
Aliases: GHSA-xpcr-7hjq-m6qm
CVSS: 5.9 (CVSS:3.1/AV:A/AC:H/PR:L/UI:N/S:U/C:L/I:H/A:L)
Published: 2024-09-27
Source: https://osv.dev/vulnerability/CVE-2024-38796
Type: osv

## Details
EDK2 contains a vulnerability in the PeCoffLoaderRelocateImage(). An Attacker may cause memory corruption due to an overflow via an adjacent network. A successful exploit of this vulnerability may lead to a loss of Confidentiality, Integrity, and/or Availability.

## References
- https://lists.debian.org/debian-lts-announce/2025/06/msg00007.html
- https://github.com/tianocore/edk2/security/advisories/GHSA-xpcr-7hjq-m6qm
- https://security.netapp.com/advisory/ntap-20241206-0006/
