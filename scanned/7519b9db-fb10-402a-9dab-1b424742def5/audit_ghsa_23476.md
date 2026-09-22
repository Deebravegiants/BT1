# [H] Command Injection in VIVO Vitro

## Summary
Severity: High
Advisory: GHSA-hgq9-q8g2-3jmg
CVE: CVE-2019-6986
CWE: CWE-400, CWE-77
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-hgq9-q8g2-3jmg
Type: github-advisory

## Affected
- Maven: `org.vivoweb:vitro-project` — affected >=0 <1.11.0

## Details
SPARQL Injection in VIVO Vitro v1.10.0 allows a remote attacker to execute arbitrary SPARQL via the uri parameter, leading to a regular expression denial of service (ReDoS), as demonstrated by crafted use of FILTER%20regex in a /individual?uri= request.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-6986
- https://github.com/vivo-project/Vitro/pull/111
- https://github.com/vivo-project/Vitro/pull/111/commits/248ef19107a5ac6f86304fd8f3bc75f3787f8d49
- https://github.com/kevinbackhouse/SecurityExploits/tree/0ec74459ac53685a7959ed58d580ef8abece3685/vivo-project
- https://github.com/vivo-project/Vitro
- https://jira.duraspace.org/browse/VIVO-1697
- http://packetstormsecurity.com/files/172838/VIVO-SPARQL-Injection.html
