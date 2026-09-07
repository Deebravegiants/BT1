# [C] Exposure of Resource to Wrong Sphere in Apache Tomcat

## Summary
Severity: Critical
Advisory: GHSA-3vx3-xf6q-r5xp
CVE: CVE-2017-5648
CWE: CWE-668
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-3vx3-xf6q-r5xp
Type: github-advisory

## Affected
- Maven: `org.apache.tomcat:tomcat-catalina` — affected >=9.0.0.M1 <9.0.0.M18
- Maven: `org.apache.tomcat:tomcat-catalina` — affected >=8.5.0 <8.5.13
- Maven: `org.apache.tomcat:tomcat-catalina` — affected >=8.0.0 <8.0.42
- Maven: `org.apache.tomcat:tomcat-catalina` — affected >=7.0.0 <7.0.76
- Maven: `org.apache.tomcat.embed:tomcat-embed-core` — affected >=9.0.0.M1 <9.0.0.M18
- Maven: `org.apache.tomcat.embed:tomcat-embed-core` — affected >=8.5.0 <8.5.13
- Maven: `org.apache.tomcat.embed:tomcat-embed-core` — affected >=8.0.0 <8.0.42
- Maven: `org.apache.tomcat.embed:tomcat-embed-core` — affected >=7.0.0 <7.0.76

## Details
While investigating bug 60718, it was noticed that some calls to application listeners in Apache Tomcat 9.0.0.M1 to 9.0.0.M17, 8.5.0 to 8.5.11, 8.0.0.RC1 to 8.0.41, and 7.0.0 to 7.0.75 did not use the appropriate facade object. When running an untrusted application under a SecurityManager, it was therefore possible for that untrusted application to retain a reference to the request or response object and thereby access and/or modify information associated with another web application.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-5648
- https://github.com/apache/tomcat/commit/0f7b9465d594b9814e1853d1e3a6e3aa51a21610
- https://github.com/apache/tomcat/commit/6bb36dfdf6444efda074893dff493b9eb3648808
- https://github.com/apache/tomcat/commit/dfa40863421d7681fed893b4256666491887e38c
- https://github.com/apache/tomcat80/commit/6d73b079c55ee25dea1bbd0556bb568a4247dacd
- https://lists.apache.org/thread.html/88855876c33f2f9c532ffb75bfee570ccf0b17ffa77493745af9a17a@%3Cdev.tomcat.apache.org%3E
- https://lists.apache.org/thread.html/b5e3f51d28cd5d9b1809f56594f2cf63dcd6a90429e16ea9f83bbedc%40%3Cdev.tomcat.apache.org%3E
- https://lists.apache.org/thread.html/b5e3f51d28cd5d9b1809f56594f2cf63dcd6a90429e16ea9f83bbedc@%3Cdev.tomcat.apache.org%3E
- https://lists.apache.org/thread.html/d0e00f2e147a9e9b13a6829133092f349b2882bf6860397368a52600%40%3Cannounce.tomcat.apache.org%3E
- https://lists.apache.org/thread.html/d0e00f2e147a9e9b13a6829133092f349b2882bf6860397368a52600@%3Cannounce.tomcat.apache.org%3E
- https://lists.apache.org/thread.html/r3bbb800a816d0a51eccc5a228c58736960a9fffafa581a225834d97d%40%3Cdev.tomcat.apache.org%3E
- https://lists.apache.org/thread.html/r3bbb800a816d0a51eccc5a228c58736960a9fffafa581a225834d97d@%3Cdev.tomcat.apache.org%3E
- https://lists.apache.org/thread.html/r48c1444845fe15a823e1374674bfc297d5008a5453788099ea14caf0%40%3Cdev.tomcat.apache.org%3E
- https://lists.apache.org/thread.html/r48c1444845fe15a823e1374674bfc297d5008a5453788099ea14caf0@%3Cdev.tomcat.apache.org%3E
- https://lists.apache.org/thread.html/r9136ff5b13e4f1941360b5a309efee2c114a14855578c3a2cbe5d19c%40%3Cdev.tomcat.apache.org%3E
- https://lists.apache.org/thread.html/r9136ff5b13e4f1941360b5a309efee2c114a14855578c3a2cbe5d19c@%3Cdev.tomcat.apache.org%3E
- https://security.gentoo.org/glsa/201705-09
- https://security.netapp.com/advisory/ntap-20180614-0001
- https://web.archive.org/web/20170417124117/http://www.securityfocus.com/bid/97530
- https://web.archive.org/web/20170420115120/http://www.securitytracker.com/id/1038220
