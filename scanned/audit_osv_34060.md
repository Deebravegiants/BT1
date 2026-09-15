# [M] CVE-2025-54363

## Summary
Severity: Medium
Advisory: CVE-2025-54363
CVSS: 6.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2025-08-20
Source: https://osv.dev/vulnerability/CVE-2025-54363
Type: osv

## Details
Microsoft Knack 0.12.0 allows Regular expression Denial of Service (ReDoS) in the knack.introspection module. extract_full_summary_from_signature employs an inefficient regular expression pattern: "\s(:param)\s+(.+?)\s:(.*)" that is susceptible to catastrophic backtracking when processing crafted docstrings containing a large volume of whitespace without a terminating colon. An attacker who can control or inject docstring content into affected applications can trigger excessive CPU consumption. This software is used by Azure CLI.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/54xxx/CVE-2025-54363.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-54363
- https://www.vulncheck.com/advisories/microsoft-knack-python-package-regular-expression-dos
- https://github.com/microsoft/knack/issues/281
- https://github.com/microsoft/knack
