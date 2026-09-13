# [H] Path Traversal in Eclipse Mojarra

## Summary
Severity: High
Advisory: GHSA-43q7-q5vp-3g68
CVE: CVE-2018-14371
CWE: CWE-22
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-43q7-q5vp-3g68
Type: github-advisory

## Affected
- Maven: `org.glassfish:mojarra-parent` — affected >=0 <2.3.7

## Details
The getLocalePrefix function in ResourceManager.java in Eclipse Mojarra before 2.3.7 is affected by Directory Traversal via the loc parameter. A remote attacker can download configuration files or Java bytecodes from applications.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-14371
- https://github.com/eclipse-ee4j/mojarra/pull/4384
- https://github.com/eclipse-ee4j/mojarra/commit/1b434748d9239f42eae8aa7d37d7a0930c061e24
