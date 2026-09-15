# [M] CVE-2024-38797

## Summary
Severity: Medium
Advisory: CVE-2024-38797
Aliases: GHSA-4wjw-6xmf-44xf
CVSS: 4.6 (CVSS:3.1/AV:A/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:L)
Published: 2025-04-07
Source: https://osv.dev/vulnerability/CVE-2024-38797
Type: osv

## Details
EDK2 contains a vulnerability in the HashPeImageByType(). A user may cause a read out of bounds when a corrupted data pointer and length are sent via an adjecent network. A successful exploit of this vulnerability may lead to a loss of Integrity and/or Availability.

## References
- https://github.com/tianocore/edk2/security/advisories/GHSA-4wjw-6xmf-44xf
