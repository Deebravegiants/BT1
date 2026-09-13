# [H] Cacti has SQL Injection via rfilter parameter in RLIKE clauses

## Summary
Severity: High
Advisory: CVE-2026-39948
Aliases: GHSA-9jqv-4cpm-vm2c
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-06-24
Source: https://osv.dev/vulnerability/CVE-2026-39948
Type: osv

## Details
Cacti is an open source performance and fault management framework. In versions 1.2.30 and prior, the rfilter request parameter is retrieved via the raw accessor grv() (rather than gfrv() with FILTER_VALIDATE_IS_REGEX validation) and concatenated directly into RLIKE SQL clauses in lib/html_graph.php and lib/html_tree.php, which are reachable pre-authentication through graph_view.php on installations with guest graph viewing enabled. Because the unbalanced-quote payload bypasses the regex validation that would otherwise reject it, an unauthenticated attacker can inject arbitrary SQL to compromise the confidentiality, integrity, and availability of the database. This advisory is similar to GHSA-69gg-mjfm-jjpc. This issue has been fixed in version 1.2.31.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/39xxx/CVE-2026-39948.json
- https://github.com/Cacti/cacti/security/advisories/GHSA-9jqv-4cpm-vm2c
- https://nvd.nist.gov/vuln/detail/CVE-2026-39948
- https://github.com/Cacti/cacti/commit/136ae6ef0715e77bca69c0eb60781f5e17df0795
