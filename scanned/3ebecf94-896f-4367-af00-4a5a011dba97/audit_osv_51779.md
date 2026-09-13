# [H] CVE-2021-40426

## Summary
Severity: High
Advisory: CVE-2021-40426
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2022-04-14
Source: https://osv.dev/vulnerability/CVE-2021-40426
Type: osv

## Details
A heap-based buffer overflow vulnerability exists in the sphere.c start_read() functionality of Sound Exchange libsox 14.4.2 and master commit 42b3557e. A specially-crafted file can lead to a heap buffer overflow. An attacker can provide a malicious file to trigger this vulnerability.

## References
- http://www.openwall.com/lists/oss-security/2023/02/03/3
- https://lists.debian.org/debian-lts-announce/2023/02/msg00009.html
- https://www.debian.org/security/2023/dsa-5356
- https://talosintelligence.com/vulnerability_reports/TALOS-2021-1434
