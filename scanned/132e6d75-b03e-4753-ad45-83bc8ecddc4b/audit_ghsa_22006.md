# [H] Race condition in Apache Tomcat

## Summary
Severity: High
Advisory: GHSA-9f3j-pm6f-9fm5
CVE: CVE-2022-23181
CWE: CWE-367
Ecosystem: Maven
CVSS: CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-02-01
Source: https://github.com/advisories/GHSA-9f3j-pm6f-9fm5
Type: github-advisory

## Affected
- Maven: `org.apache.tomcat:tomcat` — affected >=10.0.0 <10.0.16
- Maven: `org.apache.tomcat:tomcat` — affected >=9.0.0 <9.0.58
- Maven: `org.apache.tomcat:tomcat` — affected >=0 <8.5.75

## Details
The fix for bug CVE-2020-9484 introduced a time of check time of use vulnerability into Apache Tomcat 10.1.0-M1 to 10.1.0-M8, 10.0.0-M5 to 10.0.14, 9.0.35 to 9.0.56 and 8.5.55 to 8.5.73 that allowed a local attacker to perform actions with the privileges of the user that the Tomcat process is using. This issue is only exploitable when Tomcat is configured to persist sessions using the FileStore.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-23181
- https://github.com/apache/tomcat
- https://lists.apache.org/thread/l8x62p3k19yfcb208jo4zrb83k5mfwg9
- https://lists.debian.org/debian-lts-announce/2022/10/msg00029.html
- https://security.netapp.com/advisory/ntap-20220217-0010
- https://www.debian.org/security/2022/dsa-5265
- https://www.oracle.com/security-alerts/cpuapr2022.html
- https://www.oracle.com/security-alerts/cpujul2022.html
