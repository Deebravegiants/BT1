# [H] CVE-2023-39414

## Summary
Severity: High
Advisory: CVE-2023-39414
CVSS: 7.3 (CVSS:3.1/AV:L/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:H)
Published: 2024-01-08
Source: https://osv.dev/vulnerability/CVE-2023-39414
Type: osv

## Details
Multiple integer underflow vulnerabilities exist in the LXT2 lxt2_rd_iter_radix shift operation functionality of GTKWave 3.3.115. A specially crafted .lxt2 file can lead to memory corruption. A victim would need to open a malicious file to trigger these vulnerabilities.This vulnerability concerns the integer underflow when performing the right shift operation.

## References
- https://www.talosintelligence.com/vulnerability_reports/TALOS-2023-1824
- https://lists.debian.org/debian-lts-announce/2024/04/msg00007.html
- https://talosintelligence.com/vulnerability_reports/TALOS-2023-1824
