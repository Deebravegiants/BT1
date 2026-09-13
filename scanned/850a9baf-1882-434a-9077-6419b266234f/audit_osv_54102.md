# [H] CVE-2023-38648

## Summary
Severity: High
Advisory: CVE-2023-38648
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2024-01-08
Source: https://osv.dev/vulnerability/CVE-2023-38648
Type: osv

## Details
Multiple out-of-bounds write vulnerabilities exist in the VZT vzt_rd_get_facname decompression functionality of GTKWave 3.3.115. A specially crafted .vzt file can lead to arbitrary code execution. A victim would need to open a malicious file to trigger these vulnerabilities.This vulnerability concerns the out-of-bounds write perfomed by the prefix copy loop.

## References
- https://www.talosintelligence.com/vulnerability_reports/TALOS-2023-1813
- https://lists.debian.org/debian-lts-announce/2024/04/msg00007.html
- https://talosintelligence.com/vulnerability_reports/TALOS-2023-1813
