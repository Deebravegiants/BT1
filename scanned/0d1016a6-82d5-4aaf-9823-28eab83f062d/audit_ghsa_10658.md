# [M] H2O-3 is Vulnerable to Code Injection

## Summary
Severity: Medium
Advisory: GHSA-qmcv-hh7c-3m56
CVE: CVE-2026-3960
CWE: CWE-94
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-04-23
Source: https://github.com/advisories/GHSA-qmcv-hh7c-3m56
Type: github-advisory

## Affected
- Maven: `ai.h2o:h2o-core` — affected >=0 <3.46.0.10

## Details
A critical remote code execution vulnerability exists in the unauthenticated REST API endpoint /99/ImportSQLTable in H2O-3 version 3.46.0.9 and prior. The vulnerability arises due to insufficient security controls in the parameter blacklist mechanism, which only targets MySQL JDBC driver-specific dangerous parameters. An attacker can bypass these controls by switching the JDBC URL protocol to jdbc:postgresql: and exploiting PostgreSQL JDBC driver-specific parameters such as socketFactory and socketFactoryArg. This allows unauthenticated attackers to execute arbitrary code on the H2O-3 server with the privileges of the H2O-3 process. The issue is resolved in version 3.46.0.10.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-3960
- https://github.com/h2oai/h2o-3/commit/b9ae2d3c5220db2dc53753357a783e590364d044
- https://github.com/h2oai/h2o-3
- https://huntr.com/bounties/6954fe04-b905-453f-8c53-205ac8377e0d
