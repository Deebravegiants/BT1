# [C] CVE-2023-47212

## Summary
Severity: Critical
Advisory: CVE-2023-47212
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-05-01
Source: https://osv.dev/vulnerability/CVE-2023-47212
Type: osv

## Details
A heap-based buffer overflow vulnerability exists in the comment functionality of stb _vorbis.c v1.22. A specially crafted .ogg file can lead to an out-of-bounds write. An attacker can provide a malicious file to trigger this vulnerability.

## References
- https://www.talosintelligence.com/vulnerability_reports/TALOS-2023-1846
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/2MHQQXX27ACLLYUQHWSL3DVCOGUK5ZA4/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/2WRORYQ2Z2XXHPX36JHBUSDVY6IOMW2N/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/LBIPXOBWUHPAH4QHMVP2AWWAPDDZDQ66/
- https://talosintelligence.com/vulnerability_reports/TALOS-2023-1846
