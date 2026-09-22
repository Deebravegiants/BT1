# [H] CVE-2017-12109

## Summary
Severity: High
Advisory: CVE-2017-12109
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2018-04-24
Source: https://osv.dev/vulnerability/CVE-2017-12109
Type: osv

## Details
An exploitable integer overflow vulnerability exists in the xls_preparseWorkSheet function of libxls 1.4 when handling a MULRK record. A specially crafted XLS file can cause a memory corruption resulting in remote code execution. An attacker can send malicious XLS file to trigger this vulnerability.

## References
- https://www.talosintelligence.com/vulnerability_reports/TALOS-2017-0461
