# [H] CVE-2020-28589

## Summary
Severity: High
Advisory: CVE-2020-28589
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2021-08-11
Source: https://osv.dev/vulnerability/CVE-2020-28589
Type: osv

## Details
An improper array index validation vulnerability exists in the LoadObj functionality of tinyobjloader v2.0-rc1 and tinyobjloader development commit 79d4421. A specially crafted file could lead to code execution. An attacker can provide a malicious file to trigger this vulnerability.

## References
- https://talosintelligence.com/vulnerability_reports/TALOS-2020-1212
