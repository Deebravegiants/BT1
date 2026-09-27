# [H] Improper Access Control in Apache Tomcat

## Summary
Severity: High
Advisory: GHSA-mv42-px54-87jw
CVE: CVE-2016-0714
CWE: CWE-284
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-mv42-px54-87jw
Type: github-advisory

## Affected
- Maven: `org.apache.tomcat:tomcat` — affected >=9.0.0.M1 <9.0.0.M2
- Maven: `org.apache.tomcat:tomcat` — affected >=8.0.0.RC1 <8.0.32
- Maven: `org.apache.tomcat:tomcat` — affected >=7.0.0 <7.0.70
- Maven: `org.apache.tomcat:tomcat` — affected >=6.0.0 <6.0.46

## Details
The session-persistence implementation in Apache Tomcat 6.x before 6.0.45, 7.x before 7.0.68, 8.x before 8.0.31, and 9.x before 9.0.0.M2 mishandles session attributes, which allows remote authenticated users to bypass intended SecurityManager restrictions and execute arbitrary code in a privileged context via a web application that places a crafted object in a session.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-0714
- https://github.com/apache/tomcat/commit/50f1b1da794cd93b70ab5456d3c2c984408e1506
- https://github.com/apache/tomcat/commit/79e8ad03404c131009811855f9a30d8d01c0c736
- https://github.com/apache/tomcat/commit/824eb1d1ad922e7652ecf51adb2b9eebb5bb88b5
- https://github.com/apache/tomcat/commit/e1b1002129fea4033329f6f619ba219527bbbd40
- https://github.com/apache/tomcat/commit/f626da75fd59da82b14dee7b8cc46ad51eefdbe5
- https://github.com/apache/tomcat/commit/ff1b659dc366a2ad47cd8f7e3544c796a1b15e46
- https://github.com/apache/tomcat80/commit/2e5cc28052e84ba45196949ba602484221bbf33c
- https://github.com/apache/tomcat80/commit/5430f30c79383e4d2d87785468905fcb00bace58
- https://lists.apache.org/thread.html/b8a1bf18155b552dcf9a928ba808cbadad84c236d85eab3033662cfb%40%3Cdev.tomcat.apache.org%3E
- https://lists.apache.org/thread.html/b8a1bf18155b552dcf9a928ba808cbadad84c236d85eab3033662cfb@%3Cdev.tomcat.apache.org%3E
- https://lists.apache.org/thread.html/r03c597a64de790ba42c167efacfa23300c3d6c9fe589ab87fe02859c%40%3Cdev.tomcat.apache.org%3E
- https://lists.apache.org/thread.html/r03c597a64de790ba42c167efacfa23300c3d6c9fe589ab87fe02859c@%3Cdev.tomcat.apache.org%3E
- https://lists.apache.org/thread.html/r587e50b86c1a96ee301f751d50294072d142fd6dc08a8987ae9f3a9b%40%3Cdev.tomcat.apache.org%3E
- https://lists.apache.org/thread.html/r587e50b86c1a96ee301f751d50294072d142fd6dc08a8987ae9f3a9b@%3Cdev.tomcat.apache.org%3E
- https://lists.apache.org/thread.html/r9136ff5b13e4f1941360b5a309efee2c114a14855578c3a2cbe5d19c%40%3Cdev.tomcat.apache.org%3E
- https://lists.apache.org/thread.html/r9136ff5b13e4f1941360b5a309efee2c114a14855578c3a2cbe5d19c@%3Cdev.tomcat.apache.org%3E
- https://security.gentoo.org/glsa/201705-09
- https://security.netapp.com/advisory/ntap-20180531-0001
- https://web.archive.org/web/20170204045529/http://www.securityfocus.com/bid/83327
