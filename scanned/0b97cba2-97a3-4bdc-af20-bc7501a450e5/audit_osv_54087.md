# [H] CVE-2023-38583

## Summary
Severity: High
Advisory: CVE-2023-38583
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2024-01-08
Source: https://osv.dev/vulnerability/CVE-2023-38583
Type: osv

## Details
A stack-based buffer overflow vulnerability exists in the LXT2 lxt2_rd_expand_integer_to_bits function of GTKWave 3.3.115. A specially crafted .lxt2 file can lead to arbitrary code execution. A victim would need to open a malicious file to trigger this vulnerability.

## References
- https://lists.debian.org/debian-lts-announce/2024/04/msg00007.html
- https://www.talosintelligence.com/vulnerability_reports/TALOS-2023-1827
- https://talosintelligence.com/vulnerability_reports/TALOS-2023-1827
