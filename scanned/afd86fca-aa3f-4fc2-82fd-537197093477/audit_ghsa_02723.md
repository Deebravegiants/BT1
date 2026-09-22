# [C] Deserialization of Untrusted Data in Neo4j

## Summary
Severity: Critical
Advisory: GHSA-pc4w-8v5j-29w9
CVE: CVE-2021-34371
CWE: CWE-502
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-09-01
Source: https://github.com/advisories/GHSA-pc4w-8v5j-29w9
Type: github-advisory

## Affected
- Maven: `org.neo4j:neo4j` — affected >=0 <3.5.0

## Details
Neo4j through 3.4.18 (with the shell server enabled) exposes an RMI service that arbitrarily deserializes Java objects, e.g., through setSessionVariable. An attacker can abuse this for remote code execution because there are dependencies with exploitable gadget chains.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-34371
- https://github.com/neo4j/neo4j
- https://www.exploit-db.com/exploits/50170
