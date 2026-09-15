# [H] CVE-2023-37446

## Summary
Severity: High
Advisory: CVE-2023-37446
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2024-01-08
Source: https://osv.dev/vulnerability/CVE-2023-37446
Type: osv

## Details
Multiple out-of-bounds read vulnerabilities exist in the VCD var definition section functionality of GTKWave 3.3.115. A specially crafted .vcd file can lead to arbitrary code execution. A victim would need to open a malicious file to trigger these vulnerabilities.This vulnerability concerns the out-of-bounds write when triggered via the vcd2lxt2 conversion utility.

## References
- https://lists.debian.org/debian-lts-announce/2024/04/msg00007.html
- https://www.talosintelligence.com/vulnerability_reports/TALOS-2023-1805
- https://talosintelligence.com/vulnerability_reports/TALOS-2023-1805
