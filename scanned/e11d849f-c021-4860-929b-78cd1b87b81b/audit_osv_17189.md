# [H] CVE-2020-13531

## Summary
Severity: High
Advisory: CVE-2020-13531
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2020-12-03
Source: https://osv.dev/vulnerability/CVE-2020-13531
Type: osv

## Details
A use-after-free vulnerability exists in a way Pixar OpenUSD 20.08 processes reference paths textual USD files. A specially crafted file can trigger the reuse of a freed memory which can result in further memory corruption and arbitrary code execution. To trigger this vulnerability, the victim needs to open an attacker-provided malformed file.

## References
- https://talosintelligence.com/vulnerability_reports/TALOS-2020-1145
