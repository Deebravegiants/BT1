# [M] Improper Input Validation in Jakarta Expression Language

## Summary
Severity: Medium
Advisory: GHSA-v6w3-2prq-h95f
CVE: CVE-2021-28170
CWE: CWE-20, CWE-917
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2021-10-06
Source: https://github.com/advisories/GHSA-v6w3-2prq-h95f
Type: github-advisory

## Affected
- Maven: `com.sun.el:el-ri` — affected >=0 <3.0.4
- Maven: `org.glassfish:jakarta.el` — affected >=0 <3.0.4
- Maven: `org.glassfish:javax.el` — affected >=0

## Details
In the Jakarta Expression Language implementation 3.0.3 and earlier, a bug in the ELParserTokenManager enables invalid EL expressions to be evaluated as if they were valid.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-28170
- https://github.com/eclipse-ee4j/el-ri/issues/155
- https://github.com/eclipse-ee4j/el-ri/pull/160/commits/b6a3943ac5fba71cbc6719f092e319caa747855b
- https://github.com/eclipse-ee4j/el-ri
- https://security.snyk.io/vuln/SNYK-JAVA-ORGGLASSFISH-1297098
- https://security.snyk.io/vuln/SNYK-JAVA-ORGGLASSFISH-2841368
- https://securitylab.github.com/advisories/GHSL-2020-021-jakarta-el
- https://www.oracle.com/security-alerts/cpuapr2022.html
