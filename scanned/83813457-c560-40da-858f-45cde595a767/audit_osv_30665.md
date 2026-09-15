# [H] Cacti has a SQL Injection vulnerability when view host template

## Summary
Severity: High
Advisory: CVE-2024-54146
Aliases: GHSA-vj9g-p7f2-4wqj
CVSS: 7.6 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:H)
Published: 2025-01-27
Source: https://osv.dev/vulnerability/CVE-2024-54146
Type: osv

## Details
Cacti is an open source performance and fault management framework. Cacti has a SQL injection vulnerability in the template function of host_templates.php using the graph_template parameter. This vulnerability is fixed in 1.2.29.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/54xxx/CVE-2024-54146.json
- https://github.com/Cacti/cacti/security/advisories/GHSA-vj9g-p7f2-4wqj
- https://nvd.nist.gov/vuln/detail/CVE-2024-54146
- https://github.com/Cacti/cacti/commit/c7e4ee798d263a3209ae6e7ba182c7b65284d8f0
