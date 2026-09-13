# [H] CVE-2023-36747

## Summary
Severity: High
Advisory: CVE-2023-36747
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2024-01-08
Source: https://osv.dev/vulnerability/CVE-2023-36747
Type: osv

## Details
Multiple heap-based buffer overflow vulnerabilities exist in the fstReaderIterBlocks2 fstWritex len functionality of GTKWave 3.3.115. A specially crafted .fst file can lead to memory corruption. A victim would need to open a malicious file to trigger these vulnerabilities.This vulnerability concerns the handling of `len` in `fstWritex` when `beg_time` does not match the start of the time table.

## References
- https://lists.debian.org/debian-lts-announce/2024/04/msg00007.html
- https://www.talosintelligence.com/vulnerability_reports/TALOS-2023-1793
- https://talosintelligence.com/vulnerability_reports/TALOS-2023-1793
