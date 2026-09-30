# [H] CVE-2023-35960

## Summary
Severity: High
Advisory: CVE-2023-35960
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2024-01-08
Source: https://osv.dev/vulnerability/CVE-2023-35960
Type: osv

## Details
Multiple OS command injection vulnerabilities exist in the decompression functionality of GTKWave 3.3.115. A specially crafted wave file can lead to arbitrary command execution. A victim would need to open a malicious file to trigger these vulnerabilities.This vulnerability concerns legacy decompression in `vcd_main`.

## References
- https://lists.debian.org/debian-lts-announce/2024/04/msg00007.html
- https://www.talosintelligence.com/vulnerability_reports/TALOS-2023-1786
- https://talosintelligence.com/vulnerability_reports/TALOS-2023-1786
