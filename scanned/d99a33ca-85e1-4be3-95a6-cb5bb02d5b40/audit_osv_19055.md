# [H] CVE-2020-6155

## Summary
Severity: High
Advisory: CVE-2020-6155
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2020-11-13
Source: https://osv.dev/vulnerability/CVE-2020-6155
Type: osv

## Details
A heap overflow vulnerability exists in the Pixar OpenUSD 20.05 while parsing compressed value rep arrays in binary USD files. A specially crafted malformed file can trigger a heap overflow, which can result in remote code execution. To trigger this vulnerability, the victim needs to access an attacker-provided malformed file.

## References
- https://talosintelligence.com/vulnerability_reports/TALOS-2020-1101
