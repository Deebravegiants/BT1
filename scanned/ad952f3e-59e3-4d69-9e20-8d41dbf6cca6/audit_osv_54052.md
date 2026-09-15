# [H] CVE-2023-37573

## Summary
Severity: High
Advisory: CVE-2023-37573
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2024-01-08
Source: https://osv.dev/vulnerability/CVE-2023-37573
Type: osv

## Details
Multiple use-after-free vulnerabilities exist in the VCD get_vartoken realloc functionality of GTKWave 3.3.115. A specially crafted .vcd file can lead to arbitrary code execution. A victim would need to open a malicious file to trigger these vulnerabilities.This vulnerability concerns the use-after-free when triggered via the GUI's recoder (default) VCD parsing code.

## References
- https://lists.debian.org/debian-lts-announce/2024/04/msg00007.html
- https://www.talosintelligence.com/vulnerability_reports/TALOS-2023-1806
- https://talosintelligence.com/vulnerability_reports/TALOS-2023-1806
