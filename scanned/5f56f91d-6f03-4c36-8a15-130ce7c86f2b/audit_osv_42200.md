# [C] PyAthena SQL Injection via DefaultParameterFormatter DELETE/CTAS

## Summary
Severity: Critical
Advisory: CVE-2026-65321
Aliases: GHSA-xwj5-g6cv-4r5c
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-02
Source: https://osv.dev/vulnerability/CVE-2026-65321
Type: osv

## Details
PyAthena prior to 3.35.4 contains a sql injection vulnerability that allows unauthenticated attackers to inject arbitrary SQL by exploiting improper quote-escaping in DefaultParameterFormatter.format(), which routes DELETE and CTAS statements to the _escape_hive function that backslash-escapes single quotes rather than doubling them. Because Athena and Trino do not treat backslashes as escape characters inside string literals, attacker-supplied input such as a single quote followed by SQL syntax causes the parser to terminate the string literal prematurely, enabling data exfiltration via UNION SELECT, execution of destructive statements, and attacker-controlled CTAS destination and content.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/65xxx/CVE-2026-65321.json
- https://github.com/laughingman7743/PyAthena/security/advisories/GHSA-xwj5-g6cv-4r5c
- https://nvd.nist.gov/vuln/detail/CVE-2026-65321
- https://www.vulncheck.com/advisories/pyathena-sql-injection-via-defaultparameterformatter-delete-ctas
- https://github.com/pyathena-dev/PyAthena/commit/27901d12245ea722b3b4e211c60e2ade4e7c8efd
- https://github.com/laughingman7743/PyAthena
- https://github.com/rahulreddykarne/CVE-2026-65321-pyathena
- https://rahulkarne.com/#/cve/CVE-2026-65321
