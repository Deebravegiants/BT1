# [H] Apache Tomcat vulnerable to SecurityManager bypass

## Summary
Severity: High
Advisory: GHSA-3mjp-p938-4329
CVE: CVE-2016-6796
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-3mjp-p938-4329
Type: github-advisory

## Affected
- Maven: `org.apache.tomcat:tomcat` — affected >=9.0.0.M1 <9.0.0.M10
- Maven: `org.apache.tomcat:tomcat` — affected >=8.5.0 <8.5.5
- Maven: `org.apache.tomcat:tomcat` — affected >=8.0.0.RC1 <8.0.37
- Maven: `org.apache.tomcat:tomcat` — affected >=7.0.0 <7.0.71
- Maven: `org.apache.tomcat:tomcat` — affected >=6.0.0 <6.0.46

## Details
A malicious web application running on Apache Tomcat 9.0.0.M1 to 9.0.0.M9, 8.5.0 to 8.5.4, 8.0.0.RC1 to 8.0.36, 7.0.0 to 7.0.70 and 6.0.0 to 6.0.45 was able to bypass a configured SecurityManager via manipulation of the configuration parameters for the JSP Servlet.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-6796
- https://github.com/apache/tomcat/commit/f603f2f4595073f9490e01699d2083112a7c09a7
- https://github.com/apache/tomcat/commit/f97769f50ee2613e1bf27107a01d48907fd993ac
- https://github.com/apache/tomcat/commit/ffa0346fba2946401630291b642f1cff66d6a2be
- https://github.com/apache/tomcat80/commit/d98fa92b9dfc90fe1ffdaa3cce1be3be84532260
- https://access.redhat.com/errata/RHSA-2017:0455
- https://lists.apache.org/thread.html/845312a10aabbe2c499fca94003881d2c79fc993d85f34c1f5c77424@%3Cdev.tomcat.apache.org%3E
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
