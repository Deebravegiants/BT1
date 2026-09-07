# [H] Apache Tomcat improperly escapes input from JsonErrorReportValve

## Summary
Severity: High
Advisory: GHSA-rq2w-37h9-vg94
CVE: CVE-2022-45143
CWE: CWE-116, CWE-74
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2023-01-03
Source: https://github.com/advisories/GHSA-rq2w-37h9-vg94
Type: github-advisory

## Affected
- Maven: `org.apache.tomcat.embed:tomcat-embed-core` — affected >=8.5.83 <8.5.84
- Maven: `org.apache.tomcat.embed:tomcat-embed-core` — affected >=9.0.40 <9.0.69
- Maven: `org.apache.tomcat.embed:tomcat-embed-core` — affected >=10.1.0 <10.1.2
- Maven: `org.apache.tomcat:tomcat-catalina` — affected >=10.1.0 <10.1.2
- Maven: `org.apache.tomcat:tomcat-util` — affected >=8.5.83 <8.5.84
- Maven: `org.apache.tomcat:tomcat-util` — affected >=9.0.40 <9.0.69

## Details
The `JsonErrorReportValve` in Apache Tomcat 8.5.83, 9.0.40 to 9.0.68 and 10.1.0-M1 to 10.1.1 does not escape the `type`, `message` or `description` values. In some circumstances these are constructed from user provided data and it was therefore possible for users to supply values that invalidated or manipulated the JSON output.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-45143
- https://github.com/apache/tomcat/commit/0cab3a56bd89f70e7481bb0d68395dc7e130dbbf
- https://github.com/apache/tomcat/commit/6a0ac6a438cbbb66b6e9c5223842f53bf0cb50aa
- https://github.com/apache/tomcat/commit/b336f4e58893ea35114f1e4a415657f723b1298e
- https://github.com/apache/tomcat
- https://lists.apache.org/thread/yqkd183xrw3wqvnpcg3osbcryq85fkzj
- https://security.gentoo.org/glsa/202305-37
