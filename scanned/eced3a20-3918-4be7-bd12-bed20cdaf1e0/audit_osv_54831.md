# [H] CVE-2024-48877

## Summary
Severity: High
Advisory: CVE-2024-48877
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-06-02
Source: https://osv.dev/vulnerability/CVE-2024-48877
Type: osv

## Details
A memory corruption vulnerability exists in the Shared String Table Record Parser implementation in xls2csv utility version 0.95. A specially crafted malformed file can lead to a heap buffer overflow. An attacker can provide a malicious file to trigger this vulnerability.

## References
- https://lists.debian.org/debian-lts-announce/2025/06/msg00032.html
- https://talosintelligence.com/vulnerability_reports/TALOS-2024-2128
- https://www.talosintelligence.com/vulnerability_reports/TALOS-2024-2128
