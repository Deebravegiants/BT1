# [H] CVE-2023-35958

## Summary
Severity: High
Advisory: CVE-2023-35958
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2024-01-08
Source: https://osv.dev/vulnerability/CVE-2023-35958
Type: osv

## Details
Multiple heap-based buffer overflow vulnerabilities exist in the fstReaderIterBlocks2 VCDATA parsing functionality of GTKWave 3.3.115. A specially-crafted .fst file can lead to arbitrary code execution. A victim would need to open a malicious file to trigger these vulnerabilities.This vulnerability concerns the copy function `fstFread`.

## References
- https://www.talosintelligence.com/vulnerability_reports/TALOS-2023-1785
- https://lists.debian.org/debian-lts-announce/2024/04/msg00007.html
- https://talosintelligence.com/vulnerability_reports/TALOS-2023-1785
