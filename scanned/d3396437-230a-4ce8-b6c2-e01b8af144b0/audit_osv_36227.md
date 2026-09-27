# [M] SPIP < 4.4.10 Authentication Bypass via PHP Type Juggling

## Summary
Severity: Medium
Advisory: CVE-2026-22205
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-02-26
Source: https://osv.dev/vulnerability/CVE-2026-22205
Type: osv

## Details
SPIP versions prior to 4.4.10 contain an authentication bypass vulnerability caused by PHP type juggling that allows unauthenticated attackers to access protected information. Attackers can exploit loose type comparisons in authentication logic to bypass login verification and retrieve sensitive internal data.

## References
- https://git.spip.net/spip/spip
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/22xxx/CVE-2026-22205.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-22205
- https://www.vulncheck.com/advisories/spip-sql-injection-rce-via-union-php-tags
- https://blog.spip.net/Mise-a-jour-de-securite-sortie-de-SPIP-4-4-10.html
