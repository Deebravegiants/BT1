# [H] CVE-2023-34087

## Summary
Severity: High
Advisory: CVE-2023-34087
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2024-01-08
Source: https://osv.dev/vulnerability/CVE-2023-34087
Type: osv

## Details
An improper array index validation vulnerability exists in the EVCD var len parsing functionality of GTKWave 3.3.115. A specially crafted .evcd file can lead to arbitrary code execution. A victim would need to open a malicious file to trigger this vulnerability.

## References
- https://lists.debian.org/debian-lts-announce/2024/04/msg00007.html
- https://www.talosintelligence.com/vulnerability_reports/TALOS-2023-1803
- https://talosintelligence.com/vulnerability_reports/TALOS-2023-1803
