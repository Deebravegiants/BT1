# [M] CVE-2026-14978

## Summary
Severity: Medium
Advisory: CVE-2026-14978
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-08-19
Source: https://osv.dev/vulnerability/CVE-2026-14978
Type: osv

## Details
HashiCorp go-slug 0.4.0 through 0.18.2 could allow a local attacker to bypass .terraformignore exclusions and cause sensitive files to be included in Terraform slug uploads due to improper handling of Unicode normalization during path matching.

## References
- https://www.ibm.com/support/pages/node/7284170
