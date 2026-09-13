# [H] Remote Code Execution in SCIMono

## Summary
Severity: High
Advisory: GHSA-29q4-gxjq-rx5c
CVE: CVE-2021-21479
CWE: CWE-59, CWE-62, CWE-690, CWE-74, CWE-77, CWE-917
Ecosystem: Maven
Published: 2021-02-10
Source: https://github.com/advisories/GHSA-29q4-gxjq-rx5c
Type: github-advisory

## Affected
- Maven: `com.sap.scimono:scimono-server` — affected >=0 <0.0.19

## Details
### Impact
It is possible for attacker to inject and execute java expression and compromising the availability and integrity of the system.

### Patches
The issue was fixed on  [0.0.19 version](https://mvnrepository.com/artifact/com.sap.scimono/scimono-server/0.0.19)

## References
- https://github.com/SAP/scimono/security/advisories/GHSA-29q4-gxjq-rx5c
- https://nvd.nist.gov/vuln/detail/CVE-2021-21479
- https://github.com/SAP/scimono/commit/413b5d75fa94e77876af0e47be76475a23745b80
- https://mvnrepository.com/artifact/com.sap.scimono/scimono-server/0.0.19
