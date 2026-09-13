# [H] CVE-2020-13520

## Summary
Severity: High
Advisory: CVE-2020-13520
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2020-12-11
Source: https://osv.dev/vulnerability/CVE-2020-13520
Type: osv

## Details
An out of bounds memory corruption vulnerability exists in the way Pixar OpenUSD 20.05 reconstructs paths from binary USD files. A specially crafted malformed file can trigger an out of bounds memory modification which can result in remote code execution. To trigger this vulnerability, victim needs to access an attacker-provided malformed file.

## References
- https://support.apple.com/kb/HT212011
- https://talosintelligence.com/vulnerability_reports/TALOS-2020-1120
