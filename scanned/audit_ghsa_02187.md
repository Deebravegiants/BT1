# [M] Authentication Bypass by Alternate Name in Apache Tomcat

## Summary
Severity: Medium
Advisory: GHSA-36qh-35cm-5w2w
CVE: CVE-2021-30640
CWE: CWE-116, CWE-287, CWE-289
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:H/A:N (CVSS_V3)
Published: 2021-08-13
Source: https://github.com/advisories/GHSA-36qh-35cm-5w2w
Type: github-advisory

## Affected
- Maven: `org.apache.tomcat:tomcat` — affected >=10.0.0-M1 <10.0.5
- Maven: `org.apache.tomcat:tomcat` — affected >=9.0.0M1 <9.0.45
- Maven: `org.apache.tomcat:tomcat` — affected >=8.5.0 <8.5.65

## Details
A vulnerability in the JNDI Realm of Apache Tomcat allows an attacker to authenticate using variations of a valid user name and/or to bypass some of the protection provided by the LockOut Realm. This issue affects Apache Tomcat 10.0.0-M1 to 10.0.5; 9.0.0.M1 to 9.0.45; 8.5.0 to 8.5.65.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-30640
- https://lists.apache.org/thread.html/r59f9ef03929d32120f91f4ea7e6e79edd5688d75d0a9b65fd26d1fe8%40%3Cannounce.tomcat.apache.org%3E
- https://lists.debian.org/debian-lts-announce/2021/08/msg00009.html
- https://security.gentoo.org/glsa/202208-34
- https://security.netapp.com/advisory/ntap-20210827-0007
- https://www.debian.org/security/2021/dsa-4952
- https://www.debian.org/security/2021/dsa-4986
- https://www.oracle.com//security-alerts/cpujul2021.html
- https://www.oracle.com/security-alerts/cpujan2022.html
- https://www.oracle.com/security-alerts/cpuoct2021.html
