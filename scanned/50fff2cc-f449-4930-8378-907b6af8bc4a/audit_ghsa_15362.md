# [C] rudder-server is vulnerable to SQL injection

## Summary
Severity: Critical
Advisory: GHSA-3jmm-f6jj-rcc3
CVE: CVE-2023-30625
CWE: CWE-89
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-08-05
Source: https://github.com/advisories/GHSA-3jmm-f6jj-rcc3
Type: github-advisory

## Affected
- Go: `github.com/rudderlabs/rudder-server` — affected >=0 <1.3.0-rc.1

## Details
rudder-server is part of RudderStack, an open source Customer Data Platform (CDP). Versions of rudder-server prior to 1.3.0-rc.1 are vulnerable to SQL injection. This issue may lead to Remote Code Execution (RCE) due to the `rudder` role in PostgresSQL having superuser permissions by default. Version 1.3.0-rc.1 contains patches for this issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-30625
- https://github.com/rudderlabs/rudder-server/pull/2652
- https://github.com/rudderlabs/rudder-server/pull/2663
- https://github.com/rudderlabs/rudder-server/pull/2664
- https://github.com/rudderlabs/rudder-server/commit/0d061ff2d8c16845179d215bf8012afceba12a30
- https://github.com/rudderlabs/rudder-server/commit/2f956b7eb3d5eb2de3e79d7df2c87405af25071e
- https://github.com/rudderlabs/rudder-server/commit/9c009d9775abc99e72fc470f4c4c8e8f1775e82a
- https://github.com/rudderlabs/rudder-server
- https://securitylab.github.com/advisories
- https://securitylab.github.com/advisories/GHSL-2022-097_rudder-server
- http://packetstormsecurity.com/files/173837/Rudder-Server-SQL-Injection-Remote-Code-Execution.html
