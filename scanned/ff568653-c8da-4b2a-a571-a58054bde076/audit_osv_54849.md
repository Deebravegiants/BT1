# [H] CVE-2024-52035

## Summary
Severity: High
Advisory: CVE-2024-52035
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-06-02
Source: https://osv.dev/vulnerability/CVE-2024-52035
Type: osv

## Details
An integer overflow vulnerability exists in the OLE Document File Allocation Table Parser functionality of catdoc 0.95. A specially crafted malformed file can lead to heap-based memory corruption. An attacker can provide a malicious file to trigger this vulnerability.

## References
- https://lists.debian.org/debian-lts-announce/2025/06/msg00032.html
- https://talosintelligence.com/vulnerability_reports/TALOS-2024-2131
- https://www.talosintelligence.com/vulnerability_reports/TALOS-2024-2131
