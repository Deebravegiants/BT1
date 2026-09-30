# [C] Conductor vulnerable to OS command injection through unrestricted access to Java classes

## Summary
Severity: Critical
Advisory: GHSA-8gqp-hr9g-pg62
CVE: CVE-2025-26074
CWE: CWE-78
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2025-06-30
Source: https://github.com/advisories/GHSA-8gqp-hr9g-pg62
Type: github-advisory

## Affected
- Maven: `org.conductoross:conductor-core` — affected >=0 <3.21.13

## Details
Orkes Conductor v3.21.11 allows remote attackers to execute arbitrary OS commands through unrestricted access to Java classes.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-26074
- https://github.com/conductor-oss/conductor/commit/e9816501df1e364a3d39d7fe37d6e167c40eaa1b
- https://github.com/conductor-oss/conductor
- https://github.com/conductor-oss/conductor/blob/main/core/src/main/java/com/netflix/conductor/core/events/ScriptEvaluator.java
- https://medium.com/@mrcnry/cve-2025-26074-remote-code-execution-in-conductor-oss-via-inline-javascript-injection-5ce3cb651cfb
