# [C] SNMP4J-Agent allows a remote attacker to execute arbitrary code via the snmp4jCfgStoragePath component

## Summary
Severity: Critical
Advisory: GHSA-7h7j-7vwp-cwfg
CVE: CVE-2026-39006
CWE: CWE-73
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-06-15
Source: https://github.com/advisories/GHSA-7h7j-7vwp-cwfg
Type: github-advisory

## Affected
- Maven: `org.snmp4j:snmp4j-agent` — affected >=0

## Details
An issue in SNMP4J-Agent 3.8.3 allows a remote attacker to execute arbitrary code via the snmp4jCfgStoragePath component.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-39006
- https://github.com/EaEa0001/security-advisories/blob/main/CVE-2026-39006.md
- scm:git:git@nmp.app:snmp4j-agent.git
