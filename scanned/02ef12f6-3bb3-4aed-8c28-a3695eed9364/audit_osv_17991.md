# [H] CVE-2020-22390

## Summary
Severity: High
Advisory: CVE-2020-22390
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2021-06-21
Source: https://osv.dev/vulnerability/CVE-2020-22390
Type: osv

## Details
Akaunting <= 2.0.9 is vulnerable to CSV injection in the Item name field, export function. Attackers can inject arbitrary code into the name parameter and perform code execution when the crafted file is opened.

## References
- https://cqinfo.la/csv-injection-in-akaunting/
