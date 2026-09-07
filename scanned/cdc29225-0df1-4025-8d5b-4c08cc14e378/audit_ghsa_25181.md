# [M] Observable Discrepancy in Apache Tomcat

## Summary
Severity: Medium
Advisory: GHSA-wxcp-f2c8-x6xv
CVE: CVE-2016-0762
CWE: CWE-203
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-wxcp-f2c8-x6xv
Type: github-advisory

## Affected
- Maven: `org.apache.tomcat:tomcat` — affected >=9.0.0M1 <9.0.0.M10
- Maven: `org.apache.tomcat:tomcat` — affected >=8.5.0 <8.5.5
- Maven: `org.apache.tomcat:tomcat` — affected >=8.0.0.RC1 <8.0.37
- Maven: `org.apache.tomcat:tomcat` — affected >=7.0.0 <7.0.72
- Maven: `org.apache.tomcat:tomcat` — affected >=6.0.0 <6.0.46

## Details
The Realm implementations in Apache Tomcat versions 9.0.0.M1 to 9.0.0.M9, 8.5.0 to 8.5.4, 8.0.0.RC1 to 8.0.36, 7.0.0 to 7.0.70 and 6.0.0 to 6.0.45 did not process the supplied password if the supplied user name did not exist. This made a timing attack possible to determine valid user names. Note that the default configuration includes the LockOutRealm which makes exploitation of this vulnerability harder.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-0762
- https://github.com/apache/tomcat/commit/86b2e436099cb48f30dad950175c5beeeb763756
- https://github.com/apache/tomcat/commit/970e615c7ade6ec6c341470bbc76aa1256353737
- https://github.com/apache/tomcat/commit/d79c63d424fe6b225678416343b9ce106dec947c
- https://github.com/apache/tomcat80/commit/dc4c3317452f0bc2c5e1f6a08d3bd9f22488b450
- https://access.redhat.com/errata/RHSA-2017:0455
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
- https://usn.ubuntu.com/4557-1
