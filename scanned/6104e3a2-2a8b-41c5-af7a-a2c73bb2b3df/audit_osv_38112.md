# [C] OpenProject: SQL Injection in Cost Reporting =n Operator via parse_number_string

## Summary
Severity: Critical
Advisory: CVE-2026-34717
Aliases: GHSA-5rrm-6qmq-2364
CVSS: 9.9 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:L/I:H/A:H)
Published: 2026-04-02
Source: https://osv.dev/vulnerability/CVE-2026-34717
Type: osv

## Details
OpenProject is an open-source, web-based project management software. Prior to version 17.2.3, the =n operator in modules/reporting/lib/report/operator.rb:177 embeds user input directly into SQL WHERE clauses without parameterization. This issue has been patched in version 17.2.3.

## References
- https://github.com/opf/openproject/releases/tag/v17.2.3
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/34xxx/CVE-2026-34717.json
- https://github.com/opf/openproject/security/advisories/GHSA-5rrm-6qmq-2364
- https://nvd.nist.gov/vuln/detail/CVE-2026-34717
