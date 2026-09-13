# [H] CVE-2020-6156

## Summary
Severity: High
Advisory: CVE-2020-6156
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2020-11-13
Source: https://osv.dev/vulnerability/CVE-2020-6156
Type: osv

## Details
A heap overflow vulnerability exists in Pixar OpenUSD 20.05 when the software parses compressed sections in binary USD files. To trigger this vulnerability, the victim needs to open an attacker-provided malformed file in an instance USDC file format path element token index.

## References
- https://talosintelligence.com/vulnerability_reports/TALOS-2020-1094
