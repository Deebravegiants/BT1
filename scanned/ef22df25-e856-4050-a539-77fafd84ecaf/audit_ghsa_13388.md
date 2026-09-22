# [H] Apache Tomcat - Fix for CVE-2023-24998 was incomplete

## Summary
Severity: High
Advisory: GHSA-cx6h-86xw-9x34
CVE: CVE-2023-28709
CWE: CWE-193
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2023-07-06
Source: https://github.com/advisories/GHSA-cx6h-86xw-9x34
Type: github-advisory

## Affected
- Maven: `org.apache.tomcat.embed:tomcat-embed-core` — affected >=11.0.0-M2 <11.0.0-M5
- Maven: `org.apache.tomcat.embed:tomcat-embed-core` — affected >=10.1.5 <10.1.8
- Maven: `org.apache.tomcat.embed:tomcat-embed-core` — affected >=9.0.71 <9.0.74
- Maven: `org.apache.tomcat:tomcat-coyote` — affected >=8.5.85 <8.5.88

## Details
The fix for CVE-2023-24998 was incomplete. If non-default HTTP connector settings were used such that the maxParameterCount could be reached using query string parameters and a request was submitted that supplied exactly maxParameterCount parameters in the query string, the limit for uploaded request parts could be bypassed with the potential for a denial of service to occur.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-28709
- https://github.com/apache/tomcat/commit/5badf94e79e5de206fc0ef3054fd536b1bb787cd
- https://github.com/apache/tomcat/commit/ba848da71c523d94950d3c53c19ea155189df9dc
- https://github.com/apache/tomcat/commit/d53d8e7f77042cc32a3b98f589496a1ef5088e38
- https://github.com/apache/tomcat/commit/fbd81421629afe8b8a3922d59020cde81caea861
- https://github.com/apache/tomcat
- https://lists.apache.org/thread/7wvxonzwb7k9hx9jt3q33cmy7j97jo3j
- https://security.gentoo.org/glsa/202305-37
- https://security.netapp.com/advisory/ntap-20230616-0004
- https://tomcat.apache.org/security-10.html
- https://tomcat.apache.org/security-11.html
- https://tomcat.apache.org/security-8.html
- https://tomcat.apache.org/security-9.html
- https://www.debian.org/security/2023/dsa-5521
- http://www.openwall.com/lists/oss-security/2023/05/22/1
