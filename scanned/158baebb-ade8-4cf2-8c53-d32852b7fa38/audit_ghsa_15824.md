# [C] JSONPath Plus Remote Code Execution (RCE) Vulnerability

## Summary
Severity: Critical
Advisory: GHSA-pppg-cpfq-h7wr
CVE: CVE-2024-21534
CWE: CWE-94
Ecosystem: Maven, npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-10-11
Source: https://github.com/advisories/GHSA-pppg-cpfq-h7wr
Type: github-advisory

## Affected
- npm: `jsonpath-plus` — affected >=0 <10.2.0
- Maven: `org.webjars.npm:jsonpath-plus` — affected >=0

## Details
Versions of the package jsonpath-plus before 10.0.7 are vulnerable to Remote Code Execution (RCE) due to improper input sanitization. An attacker can execute aribitrary code on the system by exploiting the unsafe default usage of vm in Node.

**Note:**

There were several attempts to fix it in versions [10.0.0-10.1.0](https://github.com/JSONPath-Plus/JSONPath/compare/v9.0.0...v10.1.0) but it could still be exploited using [different payloads](https://github.com/JSONPath-Plus/JSONPath/issues/226)

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-21534
- https://github.com/JSONPath-Plus/JSONPath/issues/226
- https://github.com/JSONPath-Plus/JSONPath/issues/226#issuecomment-2424230316
- https://github.com/JSONPath-Plus/JSONPath/pull/233
- https://github.com/JSONPath-Plus/JSONPath/commit/6b2f1b4c234292c75912b790bf7e2d7339d4ccd3
- https://github.com/JSONPath-Plus/JSONPath/commit/73ad72e5ee788d8287dea6e8283a3f16f63c9eb8
- https://github.com/JSONPath-Plus/JSONPath/commit/b70aa713553caf838a63bac923195a5bc541fd72
- https://github.com/JSONPath-Plus/JSONPath
- https://github.com/JSONPath-Plus/JSONPath/compare/v9.0.0...v10.1.0
- https://security.snyk.io/vuln/SNYK-JAVA-ORGWEBJARSNPM-8185019
- https://security.snyk.io/vuln/SNYK-JS-JSONPATHPLUS-7945884
