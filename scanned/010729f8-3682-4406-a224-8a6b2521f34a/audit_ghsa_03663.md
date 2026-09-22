# [H] Improper Locking in Apache Tomcat

## Summary
Severity: High
Advisory: GHSA-q4hg-rmq2-52q9
CVE: CVE-2019-10072
CWE: CWE-667
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2019-06-26
Source: https://github.com/advisories/GHSA-q4hg-rmq2-52q9
Type: github-advisory

## Affected
- Maven: `org.apache.tomcat.embed:tomcat-embed-core` — affected >=9.0.0.M1 <9.0.20
- Maven: `org.apache.tomcat.embed:tomcat-embed-core` — affected >=8.5.0 <8.5.41

## Details
The fix for CVE-2019-0199 was incomplete and did not address HTTP/2 connection window exhaustion on write in Apache Tomcat versions 9.0.0.M1 to 9.0.19 and 8.5.0 to 8.5.40 . By not sending WINDOW_UPDATE messages for the connection window (stream 0) clients were able to cause server-side threads to block eventually leading to thread exhaustion and a DoS.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-10072
- https://github.com/apache/tomcat/commit/0bcd69c9dd8ae0ff424f2cd46de51583510b7f35
- https://github.com/apache/tomcat/commit/7f748eb6bfaba5207c89dbd7d5adf50fae847145
- https://github.com/apache/tomcat/commit/8d14c6f21d29768a39be4b6b9517060dc6606758
- https://github.com/apache/tomcat/commit/ada725a50a60867af3422c8e612aecaeea856a9a
- https://security.netapp.com/advisory/ntap-20190625-0002
- https://support.f5.com/csp/article/K17321505
- https://tomcat.apache.org/security-8.html
- https://tomcat.apache.org/security-9.html
- https://usn.ubuntu.com/4128-1
- https://usn.ubuntu.com/4128-2
- https://web.archive.org/web/20200227033743/http://www.securityfocus.com/bid/108874
- https://www.debian.org/security/2020/dsa-4680
- https://www.oracle.com/security-alerts/cpuApr2021.html
- https://www.oracle.com/security-alerts/cpuapr2020.html
- https://www.oracle.com/security-alerts/cpujan2020.html
- https://www.oracle.com/security-alerts/cpuoct2020.html
- https://www.oracle.com/technetwork/security-advisory/cpuoct2019-5072832.html
- https://www.synology.com/security/advisory/Synology_SA_19_29
- https://lists.apache.org/thread.html/raba0fabaf4d56d4325ab2aca8814f0b30a237ab83d8106b115ee279a@%3Cdev.tomcat.apache.org%3E
