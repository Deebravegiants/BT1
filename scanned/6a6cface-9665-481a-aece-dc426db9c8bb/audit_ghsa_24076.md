# [M] System Property Disclosure in Apache Tomcat

## Summary
Severity: Medium
Advisory: GHSA-2rvf-329f-p99g
CVE: CVE-2016-6794
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-2rvf-329f-p99g
Type: github-advisory

## Affected
- Maven: `org.apache.tomcat:tomcat` — affected >=6.0.0 <6.0.47
- Maven: `org.apache.tomcat:tomcat` — affected >=7.0.0 <7.0.72
- Maven: `org.apache.tomcat:tomcat` — affected >=8.0.0 <8.0.37
- Maven: `org.apache.tomcat:tomcat` — affected >=8.1.0 <8.5.5
- Maven: `org.apache.tomcat:tomcat` — affected >=9.0.0.M1 <9.0.0.M10

## Details
When a SecurityManager is configured, a web application's ability to read system properties should be controlled by the SecurityManager. In Apache Tomcat 9.0.0.M1 to 9.0.0.M9, 8.5.0 to 8.5.4, 8.0.0.RC1 to 8.0.36, 7.0.0 to 7.0.70, 6.0.0 to 6.0.45 the system property replacement feature for configuration files could be used by a malicious web application to bypass the SecurityManager and read system properties that should not be visible.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-6794
- https://github.com/apache/tomcat/commit/0b41766456b1980e4f809e13ad6dc9fa912bae7e
- https://github.com/apache/tomcat/commit/c1660182010b4255c21c874d69c124370a67784a
- https://github.com/apache/tomcat/commit/f8db078f1e6e8b225f8344e63595113ca34cd408
- https://github.com/apache/tomcat80/commit/ae6163a4f230bc679abfc93e048ff92996badad6
- https://lists.apache.org/thread.html/88855876c33f2f9c532ffb75bfee570ccf0b17ffa77493745af9a17a%40%3Cdev.tomcat.apache.org%3E
- https://lists.apache.org/thread.html/88855876c33f2f9c532ffb75bfee570ccf0b17ffa77493745af9a17a@%3Cdev.tomcat.apache.org%3E
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
