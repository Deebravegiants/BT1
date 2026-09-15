# [H] Incorrect Authorization in Apache Tomcat

## Summary
Severity: High
Advisory: GHSA-q6x7-f33r-3wxx
CVE: CVE-2016-6797
CWE: CWE-863
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-q6x7-f33r-3wxx
Type: github-advisory

## Affected
- Maven: `org.apache.tomcat:tomcat` — affected >=9.0.0.M1 <9.0.0.M10
- Maven: `org.apache.tomcat:tomcat` — affected >=8.5.0 <8.5.5
- Maven: `org.apache.tomcat:tomcat` — affected >=8.0.0 <8.0.37
- Maven: `org.apache.tomcat:tomcat` — affected >=7.0.0 <7.0.72

## Details
The ResourceLinkFactory implementation in Apache Tomcat 9.0.0.M1 to 9.0.0.M9, 8.5.0 to 8.5.4, 8.0.0.RC1 to 8.0.36, 7.0.0 to 7.0.70 and 6.0.0 to 6.0.45 did not limit web application access to global JNDI resources to those resources explicitly linked to the web application. Therefore, it was possible for a web application to access any global JNDI resource whether an explicit ResourceLink had been configured or not.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-6797
- https://github.com/apache/tomcat/commit/2859ac3eae132383cb6f3f2042e25d7a4a281b0d
- https://github.com/apache/tomcat/commit/b3406e6c318378cbf440f902f9fdbb8b440aef4e
- https://github.com/apache/tomcat/commit/d6b5600afe75e1086dd564344e1d085966e4237d
- https://github.com/apache/tomcat80/commit/824c7dc781056442046db0ae34bcf1497f23f44c
- https://lists.apache.org/thread.html/9325837eb00cba5752c092047433c7f0415134d16e7f391447ff4352%40%3Cannounce.tomcat.apache.org%3E
- https://lists.apache.org/thread.html/9325837eb00cba5752c092047433c7f0415134d16e7f391447ff4352@%3Cannounce.tomcat.apache.org%3E
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
- https://security.netapp.com/advisory/ntap-20180605-0001
