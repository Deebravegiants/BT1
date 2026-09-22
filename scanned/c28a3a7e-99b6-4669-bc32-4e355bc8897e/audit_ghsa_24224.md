# [M] Apache Tomcat Vulnerable to Denial of Service (DoS) via Improper Handling of chunk extensions

## Summary
Severity: Medium
Advisory: GHSA-qfxv-3ppc-7qg5
CVE: CVE-2012-3544
CWE: CWE-20
Ecosystem: Maven
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-qfxv-3ppc-7qg5
Type: github-advisory

## Affected
- Maven: `org.apache.tomcat:tomcat` — affected >=6.0.0 <6.0.37
- Maven: `org.apache.tomcat:tomcat` — affected >=7.0.0 <7.0.30

## Details
Apache Tomcat 6.x before 6.0.37 and 7.x before 7.0.30 does not properly handle chunk extensions in chunked transfer coding, which allows remote attackers to cause a denial of service by streaming data.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2012-3544
- https://github.com/apache/tomcat
- https://lists.apache.org/thread.html/37220405a377c0182d2afdbc36461c4783b2930fbeae3a17f1333113%40%3Cdev.tomcat.apache.org%3E
- https://lists.apache.org/thread.html/37220405a377c0182d2afdbc36461c4783b2930fbeae3a17f1333113@%3Cdev.tomcat.apache.org%3E
- https://lists.apache.org/thread.html/39ae1f0bd5867c15755a6f959b271ade1aea04ccdc3b2e639dcd903b%40%3Cdev.tomcat.apache.org%3E
- https://lists.apache.org/thread.html/39ae1f0bd5867c15755a6f959b271ade1aea04ccdc3b2e639dcd903b@%3Cdev.tomcat.apache.org%3E
- https://lists.apache.org/thread.html/b84ad1258a89de5c9c853c7f2d3ad77e5b8b2930be9e132d5cef6b95%40%3Cdev.tomcat.apache.org%3E
- https://lists.apache.org/thread.html/b84ad1258a89de5c9c853c7f2d3ad77e5b8b2930be9e132d5cef6b95@%3Cdev.tomcat.apache.org%3E
- https://lists.apache.org/thread.html/b8a1bf18155b552dcf9a928ba808cbadad84c236d85eab3033662cfb%40%3Cdev.tomcat.apache.org%3E
- https://lists.apache.org/thread.html/b8a1bf18155b552dcf9a928ba808cbadad84c236d85eab3033662cfb@%3Cdev.tomcat.apache.org%3E
- https://lists.apache.org/thread.html/r03c597a64de790ba42c167efacfa23300c3d6c9fe589ab87fe02859c%40%3Cdev.tomcat.apache.org%3E
- https://lists.apache.org/thread.html/r03c597a64de790ba42c167efacfa23300c3d6c9fe589ab87fe02859c@%3Cdev.tomcat.apache.org%3E
- https://lists.apache.org/thread.html/r587e50b86c1a96ee301f751d50294072d142fd6dc08a8987ae9f3a9b%40%3Cdev.tomcat.apache.org%3E
- https://lists.apache.org/thread.html/r587e50b86c1a96ee301f751d50294072d142fd6dc08a8987ae9f3a9b@%3Cdev.tomcat.apache.org%3E
- http://seclists.org/fulldisclosure/2014/Dec/23
- http://svn.apache.org/viewvc/tomcat/tc6.0.x/trunk/java/org/apache/coyote/http11/filters/ChunkedInputFilter.java?r1=1476592&r2=1476591&pathrev=1476592
- http://svn.apache.org/viewvc?view=revision&revision=1378702
- http://svn.apache.org/viewvc?view=revision&revision=1378921
- http://svn.apache.org/viewvc?view=revision&revision=1476592
- http://tomcat.apache.org/security-6.html
