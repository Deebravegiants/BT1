# [C] CometVisu Backend for openHAB affected by RCE through path traversal

## Summary
Severity: Critical
Advisory: GHSA-f729-58x4-gqgf
CVE: CVE-2024-42469
CWE: CWE-22
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-08-09
Source: https://github.com/advisories/GHSA-f729-58x4-gqgf
Type: github-advisory

## Affected
- Maven: `org.openhab.ui.bundles:org.openhab.ui.cometvisu` — affected >=0 <4.2.1

## Details
CometVisu's file system endpoints don't require authentication and additionally the endpoint to update an existing file is susceptible to path traversal. This makes it possible for an attacker to overwrite existing files on the openHAB instance. If the overwritten file is a shell script that is executed at a later time this vulnerability can allow remote code execution by an attacker.

This vulnerability was discovered with the help of CodeQL's [Uncontrolled data used in path expression](https://codeql.github.com/codeql-query-help/java/java-path-injection/) query.

## Impact

This issue may lead up to Remote Code Execution (RCE).

## References
- https://github.com/openhab/openhab-webui/security/advisories/GHSA-f729-58x4-gqgf
- https://nvd.nist.gov/vuln/detail/CVE-2024-42469
- https://github.com/openhab/openhab-webui/commit/630e8525835c698cf58856aa43782d92b18087f2
- https://github.com/openhab/openhab-webui
