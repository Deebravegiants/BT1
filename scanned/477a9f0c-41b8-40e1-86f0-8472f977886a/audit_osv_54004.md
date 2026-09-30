# [H] CVE-2023-35992

## Summary
Severity: High
Advisory: CVE-2023-35992
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2024-01-08
Source: https://osv.dev/vulnerability/CVE-2023-35992
Type: osv

## Details
An integer overflow vulnerability exists in the FST fstReaderIterBlocks2 vesc allocation functionality of GTKWave 3.3.115, when compiled as a 32-bit binary. A specially crafted .fst file can lead to memory corruption. A victim would need to open a malicious file to trigger this vulnerability.

## References
- https://www.talosintelligence.com/vulnerability_reports/TALOS-2023-1790
- https://lists.debian.org/debian-lts-announce/2024/04/msg00007.html
- https://talosintelligence.com/vulnerability_reports/TALOS-2023-1790
