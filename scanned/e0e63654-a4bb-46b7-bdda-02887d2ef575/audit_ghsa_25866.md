# [C] Improper Restriction of XML External Entity Reference in Liquibase

## Summary
Severity: Critical
Advisory: GHSA-jvfv-hrrc-6q72
CVE: CVE-2022-0839
CWE: CWE-611
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-03-05
Source: https://github.com/advisories/GHSA-jvfv-hrrc-6q72
Type: github-advisory

## Affected
- Maven: `org.liquibase:liquibase-core` — affected >=0 <4.8.0

## Details
The XMLChangeLogSAXParser() function in Liquibase prior to version 4.8.0 contains an issue that may lead to to Improper Restriction of XML External Entity Reference.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-0839
- https://github.com/liquibase/liquibase/commit/33d9d925082097fb1a3d2fc8e44423d964cd9381
- https://github.com/liquibase/liquibase
- https://huntr.dev/bounties/f1ae5779-b406-4594-a8a3-d089c68d6e70
- https://www.oracle.com/security-alerts/cpujul2022.html
- http://seclists.org/fulldisclosure/2025/Apr/14
