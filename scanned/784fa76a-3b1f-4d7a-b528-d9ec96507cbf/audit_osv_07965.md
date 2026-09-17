# [M] CVE-2016-0706

## Summary
Severity: Medium
Advisory: CVE-2016-0706
Aliases: GHSA-6vx3-hr43-cfrh
CVSS: 4.3 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N)
Published: 2016-02-25
Source: https://osv.dev/vulnerability/CVE-2016-0706
Type: osv

## Details
Apache Tomcat 6.x before 6.0.45, 7.x before 7.0.68, 8.x before 8.0.31, and 9.x before 9.0.0.M2 does not place org.apache.catalina.manager.StatusManagerServlet on the org/apache/catalina/core/RestrictedServlets.properties list, which allows remote authenticated users to bypass intended SecurityManager restrictions and read arbitrary HTTP requests, and consequently discover session ID values, via a crafted web application.

## References
- http://lists.opensuse.org/opensuse-security-announce/2016-03/msg00047.html
- http://lists.opensuse.org/opensuse-security-announce/2016-03/msg00069.html
- http://lists.opensuse.org/opensuse-security-announce/2016-03/msg00082.html
- http://lists.opensuse.org/opensuse-security-announce/2016-03/msg00085.html
- http://svn.apache.org/viewvc?view=revision&revision=1722800
- http://www.oracle.com/technetwork/topics/security/bulletinapr2016-2952098.html
- http://www.oracle.com/technetwork/topics/security/linuxbulletinoct2016-3090545.html
- http://www.securityfocus.com/bid/83324
- http://www.securitytracker.com/id/1035069
- https://lists.apache.org/thread.html/37220405a377c0182d2afdbc36461c4783b2930fbeae3a17f1333113%40%3Cdev.tomcat.apache.org%3E
- https://lists.apache.org/thread.html/39ae1f0bd5867c15755a6f959b271ade1aea04ccdc3b2e639dcd903b%40%3Cdev.tomcat.apache.org%3E
- https://lists.apache.org/thread.html/b84ad1258a89de5c9c853c7f2d3ad77e5b8b2930be9e132d5cef6b95%40%3Cdev.tomcat.apache.org%3E
- https://lists.apache.org/thread.html/b8a1bf18155b552dcf9a928ba808cbadad84c236d85eab3033662cfb%40%3Cdev.tomcat.apache.org%3E
- https://lists.apache.org/thread.html/r03c597a64de790ba42c167efacfa23300c3d6c9fe589ab87fe02859c%40%3Cdev.tomcat.apache.org%3E
- https://lists.apache.org/thread.html/r587e50b86c1a96ee301f751d50294072d142fd6dc08a8987ae9f3a9b%40%3Cdev.tomcat.apache.org%3E
- https://lists.apache.org/thread.html/r9136ff5b13e4f1941360b5a309efee2c114a14855578c3a2cbe5d19c%40%3Cdev.tomcat.apache.org%3E
- http://marc.info/?l=bugtraq&m=145974991225029&w=2
- http://rhn.redhat.com/errata/RHSA-2016-1089.html
- http://rhn.redhat.com/errata/RHSA-2016-2045.html
- http://rhn.redhat.com/errata/RHSA-2016-2599.html
