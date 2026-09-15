# [H] GLPI allows account takeover via SQL Injection in AJAX scripts

## Summary
Severity: High
Advisory: CVE-2024-37148
Aliases: GHSA-p626-hph9-p6fj
CVSS: 8.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N)
Published: 2024-07-10
Source: https://osv.dev/vulnerability/CVE-2024-37148
Type: osv

## Details
GLPI is an open-source asset and IT management software package that provides ITIL Service Desk features, licenses tracking and software auditing. An authenticated user can exploit a SQL injection vulnerability in some AJAX scripts to alter another user account data and take control of it. Upgrade to 10.0.16.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/37xxx/CVE-2024-37148.json
- https://github.com/glpi-project/glpi/security/advisories/GHSA-p626-hph9-p6fj
- https://nvd.nist.gov/vuln/detail/CVE-2024-37148
