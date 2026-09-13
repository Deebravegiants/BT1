# [M] CVE-2026-26745

## Summary
Severity: Medium
Advisory: CVE-2026-26745
CVSS: 5.3 (CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-02-20
Source: https://osv.dev/vulnerability/CVE-2026-26745
Type: osv

## Details
OpenSourcePOS 3.4.1 has a second order SQL Injection vulnerability in the handling of the currency_symbol configuration field. Although the input is initially stored without immediate execution, it is later concatenated into a dynamically constructed SQL query without proper sanitization or parameter binding. This allows an attacker with access to modify the currency_symbol value to inject arbitrary SQL expressions, which are executed when the affected query is subsequently processed.

## References
- https://github.com/hungnqdz/cve-research/blob/main/CVE-2026-26745.md
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/26xxx/CVE-2026-26745.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-26745
- https://github.com/opensourcepos/opensourcepos
