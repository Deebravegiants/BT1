# [H] The host name verification missing in Apache Tomcat

## Summary
Severity: High
Advisory: GHSA-46j3-r4pj-4835
CVE: CVE-2018-8034
CWE: CWE-295
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2018-10-17
Source: https://github.com/advisories/GHSA-46j3-r4pj-4835
Type: github-advisory

## Affected
- Maven: `org.apache.tomcat.embed:tomcat-embed-core` — affected >=9.0.0 <9.0.10
- Maven: `org.apache.tomcat.embed:tomcat-embed-core` — affected >=8.5.0 <8.5.32
- Maven: `org.apache.tomcat.embed:tomcat-embed-core` — affected >=8.0.0 <8.0.53
- Maven: `org.apache.tomcat.embed:tomcat-embed-core` — affected >=7.0.35 <7.0.90

## Details
The host name verification when using TLS with the WebSocket client was missing. It is now enabled by default. Versions Affected: Apache Tomcat 9.0.0.M1 to 9.0.9, 8.5.0 to 8.5.31, 8.0.0.RC1 to 8.0.52, and 7.0.35 to 7.0.88.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-8034
- https://github.com/apache/tomcat/commit/2c522795166c930741a9cecca76797bf48cb1634
- https://github.com/apache/tomcat/commit/2835bb4e030c1c741ed0847bb3b9c3822e4fbc8a
- https://lists.apache.org/thread.html/r9136ff5b13e4f1941360b5a309efee2c114a14855578c3a2cbe5d19c%40%3Cdev.tomcat.apache.org%3E
- https://lists.apache.org/thread.html/r6ccee4e849bc77df0840c7f853f6bd09d426f6741247da2b7429d5d9@%3Cdev.tomcat.apache.org%3E
- https://lists.apache.org/thread.html/r6ccee4e849bc77df0840c7f853f6bd09d426f6741247da2b7429d5d9%40%3Cdev.tomcat.apache.org%3E
- https://lists.apache.org/thread.html/r48c1444845fe15a823e1374674bfc297d5008a5453788099ea14caf0@%3Cdev.tomcat.apache.org%3E
- https://lists.apache.org/thread.html/r48c1444845fe15a823e1374674bfc297d5008a5453788099ea14caf0%40%3Cdev.tomcat.apache.org%3E
- https://lists.apache.org/thread.html/r3bbb800a816d0a51eccc5a228c58736960a9fffafa581a225834d97d@%3Cdev.tomcat.apache.org%3E
- https://lists.apache.org/thread.html/r3bbb800a816d0a51eccc5a228c58736960a9fffafa581a225834d97d%40%3Cdev.tomcat.apache.org%3E
- https://lists.apache.org/thread.html/eb6efa8d59c45a7a9eff94c4b925467d3b3fec8ba7697f3daa314b04@%3Cdev.tomcat.apache.org%3E
- https://lists.apache.org/thread.html/eb6efa8d59c45a7a9eff94c4b925467d3b3fec8ba7697f3daa314b04%40%3Cdev.tomcat.apache.org%3E
- https://lists.apache.org/thread.html/e85e83e9954f169bbb77b44baae5a33d8de878df557bb32b7f793661@%3Cdev.tomcat.apache.org%3E
- https://lists.apache.org/thread.html/e85e83e9954f169bbb77b44baae5a33d8de878df557bb32b7f793661%40%3Cdev.tomcat.apache.org%3E
- https://lists.apache.org/thread.html/b5e3f51d28cd5d9b1809f56594f2cf63dcd6a90429e16ea9f83bbedc@%3Cdev.tomcat.apache.org%3E
- https://lists.apache.org/thread.html/b5e3f51d28cd5d9b1809f56594f2cf63dcd6a90429e16ea9f83bbedc%40%3Cdev.tomcat.apache.org%3E
- https://lists.apache.org/thread.html/ac51944aef91dd5006b8510b0bef337adaccfe962fb90e7af9c22db4@%3Cissues.activemq.apache.org%3E
- https://lists.apache.org/thread.html/r9136ff5b13e4f1941360b5a309efee2c114a14855578c3a2cbe5d19c@%3Cdev.tomcat.apache.org%3E
- https://lists.apache.org/thread.html/raba0fabaf4d56d4325ab2aca8814f0b30a237ab83d8106b115ee279a%40%3Cdev.tomcat.apache.org%3E
- https://lists.apache.org/thread.html/raba0fabaf4d56d4325ab2aca8814f0b30a237ab83d8106b115ee279a@%3Cdev.tomcat.apache.org%3E
