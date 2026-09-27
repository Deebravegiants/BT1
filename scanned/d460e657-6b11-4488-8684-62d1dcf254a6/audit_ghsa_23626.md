# [M] Spring Framework Inefficient Regular Expression Complexity

## Summary
Severity: Medium
Advisory: GHSA-wjjr-h4wh-w6vv
CVE: CVE-2009-1190
CWE: CWE-1333
Ecosystem: Maven
Published: 2022-05-02
Source: https://github.com/advisories/GHSA-wjjr-h4wh-w6vv
Type: github-advisory

## Affected
- Maven: `org.springframework:spring-core` — affected >=1.1.0 <3.0.0.RELEASE

## Details
Algorithmic complexity vulnerability in the java.util.regex.Pattern.compile method in Sun Java Development Kit (JDK) before 1.6, when used with spring.jar in SpringSource Spring Framework 1.1.0 through 2.5.6 and 3.0.0.M1 through 3.0.0.M2 and dm Server 1.0.0 through 1.0.2, allows remote attackers to cause a denial of service (CPU consumption) via serializable data with a long regex string containing multiple optional groups, a related issue to CVE-2004-2540.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2009-1190
- https://bugzilla.redhat.com/show_bug.cgi?id=497161
- https://exchange.xforce.ibmcloud.com/vulnerabilities/50083
- http://www.packetstormsecurity.org/hitb06/DAY_1_-_Marc_Schoenefeld_-_Pentesting_Java_J2EE.pdf
- http://www.springsource.com/securityadvisory
