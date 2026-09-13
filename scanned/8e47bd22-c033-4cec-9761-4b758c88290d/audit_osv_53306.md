# [H] CVE-2022-36788

## Summary
Severity: High
Advisory: CVE-2022-36788
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2023-04-20
Source: https://osv.dev/vulnerability/CVE-2022-36788
Type: osv

## Details
A heap-based buffer overflow vulnerability exists in the TriangleMesh clone functionality of Slic3r libslic3r 1.3.0 and Master Commit b1a5500. A specially-crafted STL file can lead to a heap buffer overflow. An attacker can provide a malicious file to trigger this vulnerability.

## References
- https://www.talosintelligence.com/vulnerability_reports/TALOS-2022-1593
- https://talosintelligence.com/vulnerability_reports/TALOS-2022-1593
