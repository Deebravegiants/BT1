# [C] Apache Tomcat Improper Access Control vulnerability

## Summary
Severity: Critical
Advisory: GHSA-cw54-59pw-4g8c
CVE: CVE-2016-8735
CWE: CWE-284
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H/E:H (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-cw54-59pw-4g8c
Type: github-advisory

## Affected
- Maven: `org.apache.tomcat:tomcat-catalina-jmx-remote` — affected >=0 <6.0.48
- Maven: `org.apache.tomcat:tomcat-catalina-jmx-remote` — affected >=7.0.0 <7.0.73
- Maven: `org.apache.tomcat:tomcat-catalina-jmx-remote` — affected >=8.0.0 <8.0.39
- Maven: `org.apache.tomcat:tomcat-catalina-jmx-remote` — affected >=8.5.0 <8.5.7
- Maven: `org.apache.tomcat:tomcat-catalina-jmx-remote` — affected >=9.0.0.M1 <9.0.0.M12
- Maven: `org.apache.tomcat:tomcat-catalina` — affected >=0 <6.0.48
- Maven: `org.apache.tomcat:tomcat-catalina` — affected >=7.0.0 <7.0.73
- Maven: `org.apache.tomcat:tomcat-catalina` — affected >=8.0.0 <8.0.39
- Maven: `org.apache.tomcat:tomcat-catalina` — affected >=8.5.0 <8.5.7
- Maven: `org.apache.tomcat:tomcat-catalina` — affected >=9.0.0.M1 <9.0.0.M12

## Details
Remote code execution is possible with Apache Tomcat before 6.0.48, 7.x before 7.0.73, 8.x before 8.0.39, 8.5.x before 8.5.7, and 9.x before 9.0.0.M12 if JmxRemoteLifecycleListener is used and an attacker can reach JMX ports. 
The issue exists because this listener wasn't updated for consistency with the CVE-2016-3427 Oracle patch that affected credential types.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-8735
- https://github.com/apache/tomcat/commit/0e83ad3e547fc9a75a258799ef581249b40a82a6
- https://github.com/apache/tomcat/commit/292d6ccdc9edbf80859929b0af070b2ea99fa688
- https://github.com/apache/tomcat/commit/7e3a037055cca4a17e90b49399fb1bab4dd7c821
- https://github.com/apache/tomcat80/commit/0f76016a4ec45635e450ada9c84ff7ee0c5f3799
- https://lists.apache.org/thread.html/b5e3f51d28cd5d9b1809f56594f2cf63dcd6a90429e16ea9f83bbedc%40%3Cdev.tomcat.apache.org%3E
- https://lists.apache.org/thread.html/b5e3f51d28cd5d9b1809f56594f2cf63dcd6a90429e16ea9f83bbedc@%3Cdev.tomcat.apache.org%3E
- https://lists.apache.org/thread.html/b84ad1258a89de5c9c853c7f2d3ad77e5b8b2930be9e132d5cef6b95%40%3Cdev.tomcat.apache.org%3E
- https://lists.apache.org/thread.html/b84ad1258a89de5c9c853c7f2d3ad77e5b8b2930be9e132d5cef6b95@%3Cdev.tomcat.apache.org%3E
- https://lists.apache.org/thread.html/b8a1bf18155b552dcf9a928ba808cbadad84c236d85eab3033662cfb%40%3Cdev.tomcat.apache.org%3E
- https://lists.apache.org/thread.html/b8a1bf18155b552dcf9a928ba808cbadad84c236d85eab3033662cfb@%3Cdev.tomcat.apache.org%3E
- https://lists.apache.org/thread.html/r03c597a64de790ba42c167efacfa23300c3d6c9fe589ab87fe02859c%40%3Cdev.tomcat.apache.org%3E
- https://lists.apache.org/thread.html/r03c597a64de790ba42c167efacfa23300c3d6c9fe589ab87fe02859c@%3Cdev.tomcat.apache.org%3E
- https://lists.apache.org/thread.html/r587e50b86c1a96ee301f751d50294072d142fd6dc08a8987ae9f3a9b%40%3Cdev.tomcat.apache.org%3E
- https://lists.apache.org/thread.html/r587e50b86c1a96ee301f751d50294072d142fd6dc08a8987ae9f3a9b@%3Cdev.tomcat.apache.org%3E
- https://lists.apache.org/thread.html/r9136ff5b13e4f1941360b5a309efee2c114a14855578c3a2cbe5d19c%40%3Cdev.tomcat.apache.org%3E
- https://lists.apache.org/thread.html/r9136ff5b13e4f1941360b5a309efee2c114a14855578c3a2cbe5d19c@%3Cdev.tomcat.apache.org%3E
- https://security.netapp.com/advisory/ntap-20180607-0001
- https://usn.ubuntu.com/4557-1
- https://web.archive.org/web/20170423095340/http://www.securityfocus.com/bid/94463
