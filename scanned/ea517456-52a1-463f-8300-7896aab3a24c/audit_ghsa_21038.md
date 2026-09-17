# [C] Nepxion Discovery vulnerable to SpEL Injection leading to Remote Code Execution

## Summary
Severity: Critical
Advisory: GHSA-q979-9m39-23mq
CVE: CVE-2022-23463
CWE: CWE-917
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:L (CVSS_V3)
Published: 2022-09-25
Source: https://github.com/advisories/GHSA-q979-9m39-23mq
Type: github-advisory

## Affected
- Maven: `com.nepxion:discovery` — affected >=0

## Details
Nepxion Discovery is a solution for Spring Cloud. Discovery is vulnerable to SpEL Injection in discovery-commons. DiscoveryExpressionResolver’s eval method is evaluating expression with a StandardEvaluationContext, allowing the expression to reach and interact with Java classes such as java.lang.Runtime, leading to Remote Code Execution. There is no patch available for this issue at time of publication. There are no known workarounds.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-23463
- https://github.com/Nepxion/Discovery
- https://securitylab.github.com/advisories/GHSL-2022-033_GHSL-2022-034_Discovery
