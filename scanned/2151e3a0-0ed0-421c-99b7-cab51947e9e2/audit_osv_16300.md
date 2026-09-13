# [H] CVE-2019-5063

## Summary
Severity: High
Advisory: CVE-2019-5063
Aliases: GHSA-m6vm-8g8v-xfjh, PYSEC-2026-2801, PYSEC-2026-2826, PYSEC-2026-2840, PYSEC-2026-724
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2020-01-03
Source: https://osv.dev/vulnerability/CVE-2019-5063
Type: osv

## Details
An exploitable heap buffer overflow vulnerability exists in the data structure persistence functionality of OpenCV 4.1.0. A specially crafted XML file can cause a buffer overflow, resulting in multiple heap corruptions and potential code execution. An attacker can provide a specially crafted file to trigger this vulnerability.

## References
- https://www.oracle.com//security-alerts/cpujul2021.html
- https://www.oracle.com/security-alerts/cpuApr2021.html
- https://talosintelligence.com/vulnerability_reports/TALOS-2019-0852
