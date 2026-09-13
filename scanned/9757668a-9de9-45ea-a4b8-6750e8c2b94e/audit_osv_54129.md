# [H] CVE-2023-39275

## Summary
Severity: High
Advisory: CVE-2023-39275
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2024-01-08
Source: https://osv.dev/vulnerability/CVE-2023-39275
Type: osv

## Details
Multiple integer overflow vulnerabilities exist in the LXT2 facgeometry parsing functionality of GTKWave 3.3.115. A specially crafted .lxt2 file can lead to arbitrary code execution. A victim would need to open a malicious file to trigger these vulnerabilities.This vulnerability concerns the integer overflow when allocating the `value` array.

## References
- https://lists.debian.org/debian-lts-announce/2024/04/msg00007.html
- https://www.talosintelligence.com/vulnerability_reports/TALOS-2023-1818
- https://talosintelligence.com/vulnerability_reports/TALOS-2023-1818
