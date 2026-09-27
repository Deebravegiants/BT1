# [H] Sqlite-jdbc vulnerable to remote code execution when JDBC url is attacker controlled

## Summary
Severity: High
Advisory: GHSA-6phf-6h5g-97j2
CVE: CVE-2023-32697
CWE: CWE-94
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-05-23
Source: https://github.com/advisories/GHSA-6phf-6h5g-97j2
Type: github-advisory

## Affected
- Maven: `org.xerial:sqlite-jdbc` — affected >=3.6.14.1 <3.41.2.2

## Details
## Summary

Sqlite-jdbc addresses a remote code execution vulnerability via JDBC URL. 

## Impacted versions : 

3.6.14.1-3.41.2.1
 
## References

https://github.com/xerial/sqlite-jdbc/releases/tag/3.41.2.2

## References
- https://github.com/xerial/sqlite-jdbc/security/advisories/GHSA-6phf-6h5g-97j2
- https://nvd.nist.gov/vuln/detail/CVE-2023-32697
- https://github.com/xerial/sqlite-jdbc
- https://github.com/xerial/sqlite-jdbc/releases/tag/3.41.2.2
