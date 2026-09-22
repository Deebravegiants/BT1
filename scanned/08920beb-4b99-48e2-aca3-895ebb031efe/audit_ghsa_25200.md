# [M] Inconsistent documentation in Apache Tomcat

## Summary
Severity: Medium
Advisory: GHSA-372q-33vh-8mpc
CVE: CVE-2017-15706
CWE: CWE-1068, CWE-358
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-372q-33vh-8mpc
Type: github-advisory

## Affected
- Maven: `org.apache.tomcat:tomcat` — affected >=9.0.0.M22 <9.0.2
- Maven: `org.apache.tomcat:tomcat` — affected >=8.5.16 <8.5.24
- Maven: `org.apache.tomcat:tomcat` — affected >=8.0.45 <8.0.48
- Maven: `org.apache.tomcat:tomcat` — affected >=7.0.79 <7.0.84

## Details
As part of the fix for bug 61201, the documentation for Apache Tomcat 9.0.0.M22 to 9.0.1, 8.5.16 to 8.5.23, 8.0.45 to 8.0.47 and 7.0.79 to 7.0.82 included an updated description of the search algorithm used by the CGI Servlet to identify which script to execute. The update was not correct. As a result, some scripts may have failed to execute as expected and other scripts may have been executed unexpectedly. Note that the behaviour of the CGI servlet has remained unchanged in this regard. It is only the documentation of the behaviour that was wrong and has been corrected.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-15706
- https://github.com/apache/tomcat
- https://lists.apache.org/thread.html/e1ef853fc0079cdb55befbd2dac042934e49288b476d5f6a649e5da2@%3Cannounce.tomcat.apache.org%3E
- https://lists.apache.org/thread.html/e85e83e9954f169bbb77b44baae5a33d8de878df557bb32b7f793661%40%3Cdev.tomcat.apache.org%3E
- https://lists.apache.org/thread.html/e85e83e9954f169bbb77b44baae5a33d8de878df557bb32b7f793661@%3Cdev.tomcat.apache.org%3E
- https://lists.apache.org/thread.html/eb6efa8d59c45a7a9eff94c4b925467d3b3fec8ba7697f3daa314b04%40%3Cdev.tomcat.apache.org%3E
- https://lists.apache.org/thread.html/eb6efa8d59c45a7a9eff94c4b925467d3b3fec8ba7697f3daa314b04@%3Cdev.tomcat.apache.org%3E
- https://lists.apache.org/thread.html/r3bbb800a816d0a51eccc5a228c58736960a9fffafa581a225834d97d%40%3Cdev.tomcat.apache.org%3E
- https://lists.apache.org/thread.html/r3bbb800a816d0a51eccc5a228c58736960a9fffafa581a225834d97d@%3Cdev.tomcat.apache.org%3E
- https://lists.apache.org/thread.html/r48c1444845fe15a823e1374674bfc297d5008a5453788099ea14caf0%40%3Cdev.tomcat.apache.org%3E
- https://lists.apache.org/thread.html/r48c1444845fe15a823e1374674bfc297d5008a5453788099ea14caf0@%3Cdev.tomcat.apache.org%3E
- https://lists.apache.org/thread.html/r6ccee4e849bc77df0840c7f853f6bd09d426f6741247da2b7429d5d9%40%3Cdev.tomcat.apache.org%3E
- https://lists.apache.org/thread.html/r6ccee4e849bc77df0840c7f853f6bd09d426f6741247da2b7429d5d9@%3Cdev.tomcat.apache.org%3E
- https://lists.apache.org/thread.html/r9136ff5b13e4f1941360b5a309efee2c114a14855578c3a2cbe5d19c%40%3Cdev.tomcat.apache.org%3E
- https://lists.apache.org/thread.html/r9136ff5b13e4f1941360b5a309efee2c114a14855578c3a2cbe5d19c@%3Cdev.tomcat.apache.org%3E
- https://lists.apache.org/thread.html/raba0fabaf4d56d4325ab2aca8814f0b30a237ab83d8106b115ee279a%40%3Cdev.tomcat.apache.org%3E
- https://lists.apache.org/thread.html/raba0fabaf4d56d4325ab2aca8814f0b30a237ab83d8106b115ee279a@%3Cdev.tomcat.apache.org%3E
- https://usn.ubuntu.com/3665-1
- https://web.archive.org/web/20200227102806/http://www.securityfocus.com/bid/103069
- https://www.oracle.com/security-alerts/cpuapr2020.html
