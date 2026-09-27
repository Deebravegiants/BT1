# [M] CVE-2020-13524

## Summary
Severity: Medium
Advisory: CVE-2020-13524
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2020-12-03
Source: https://osv.dev/vulnerability/CVE-2020-13524
Type: osv

## Details
An out-of-bounds memory corruption vulnerability exists in the way Pixar OpenUSD 20.05 uses SPECS data from binary USD files. A specially crafted malformed file can trigger an out-of-bounds memory access and modification which results in memory corruption. To trigger this vulnerability, the victim needs to access an attacker-provided malformed file.

## References
- http://seclists.org/fulldisclosure/2020/Dec/26
- http://seclists.org/fulldisclosure/2020/Dec/32
- https://support.apple.com/kb/HT212011
- https://talosintelligence.com/vulnerability_reports/TALOS-2020-1125
