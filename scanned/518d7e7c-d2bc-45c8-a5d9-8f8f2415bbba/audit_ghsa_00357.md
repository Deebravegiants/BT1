# [C] Incorrect access control in Neo4j Enterprise Database Server via LDAP authentication

## Summary
Severity: Critical
Advisory: GHSA-h5f5-rj4r-42f6
CVE: CVE-2018-18389
CWE: CWE-287
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2018-10-17
Source: https://github.com/advisories/GHSA-h5f5-rj4r-42f6
Type: github-advisory

## Affected
- Maven: `org.neo4j:neo4j-enterprise` — affected >=3.4.0 <3.4.9

## Details
Due to incorrect access control in Neo4j Enterprise Database Server 3.4.x before 3.4.9, the setting of LDAP for authentication with STARTTLS, and System Account for authorization, allows an attacker to log into the server by sending any valid username with an arbitrary password.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-18389
- https://github.com/neo4j/neo4j/issues/12047
- https://github.com/neo4j/neo4j/commit/46de5d01ae2741ffe04c36270fc62c6d490f65c9
- https://github.com/advisories/GHSA-h5f5-rj4r-42f6
- https://github.com/neo4j/neo4j
