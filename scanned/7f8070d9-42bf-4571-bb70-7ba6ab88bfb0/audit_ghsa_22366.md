# [M] Insufficient Verification of Data Authenticity in Apache Tomcat

## Summary
Severity: Medium
Advisory: GHSA-73rx-3f9r-x949
CVE: CVE-2017-7674
CWE: CWE-345
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-73rx-3f9r-x949
Type: github-advisory

## Affected
- Maven: `org.apache.tomcat:tomcat` — affected >=9.0.0.M1 <9.0.0.M22
- Maven: `org.apache.tomcat:tomcat` — affected >=8.5.0 <8.5.16
- Maven: `org.apache.tomcat:tomcat` — affected >=8.0.0.RC1 <8.0.45
- Maven: `org.apache.tomcat:tomcat` — affected >=7.0.41 <7.0.79

## Details
The CORS Filter in Apache Tomcat 9.0.0.M1 to 9.0.0.M21, 8.5.0 to 8.5.15, 8.0.0.RC1 to 8.0.44 and 7.0.41 to 7.0.78 did not add an HTTP Vary header indicating that the response varies depending on Origin. This permitted client and server side cache poisoning in some circumstances.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-7674
- https://github.com/apache/tomcat/commit/52382ebfbce20a98b01cd9d37184a12703987a5a
- https://github.com/apache/tomcat/commit/9044c1672bbe4b2cf4c55028cc8b977cc62650e7
- https://github.com/apache/tomcat/commit/b94478d45b7e1fc06134a785571f78772fa30fed
- https://github.com/apache/tomcat80/commit/f52c242d92d4563dd1226dcc993ec37370ba9ce3
- https://lists.apache.org/thread.html/r6ccee4e849bc77df0840c7f853f6bd09d426f6741247da2b7429d5d9%40%3Cdev.tomcat.apache.org%3E
- https://lists.apache.org/thread.html/r48c1444845fe15a823e1374674bfc297d5008a5453788099ea14caf0@%3Cdev.tomcat.apache.org%3E
- https://lists.apache.org/thread.html/r48c1444845fe15a823e1374674bfc297d5008a5453788099ea14caf0%40%3Cdev.tomcat.apache.org%3E
- https://lists.apache.org/thread.html/r409efdf706c2077ae5c37018a87da725a3ca89570a9530342cdc53e4@%3Cusers.tomcat.apache.org%3E
- https://lists.apache.org/thread.html/r409efdf706c2077ae5c37018a87da725a3ca89570a9530342cdc53e4%40%3Cusers.tomcat.apache.org%3E
- https://lists.apache.org/thread.html/r3bbb800a816d0a51eccc5a228c58736960a9fffafa581a225834d97d@%3Cdev.tomcat.apache.org%3E
- https://lists.apache.org/thread.html/r3bbb800a816d0a51eccc5a228c58736960a9fffafa581a225834d97d%40%3Cdev.tomcat.apache.org%3E
- https://lists.apache.org/thread.html/r1c62634b7426bee5f553307063457b99c84af73b078ede4f2592b34e@%3Cusers.tomcat.apache.org%3E
- https://lists.apache.org/thread.html/r1c62634b7426bee5f553307063457b99c84af73b078ede4f2592b34e%40%3Cusers.tomcat.apache.org%3E
- https://lists.apache.org/thread.html/r15695e6203b026c9e9070ca9fa95fb17dd4cd88e5342a7dc5e1e7b85@%3Cusers.tomcat.apache.org%3E
- https://lists.apache.org/thread.html/r15695e6203b026c9e9070ca9fa95fb17dd4cd88e5342a7dc5e1e7b85%40%3Cusers.tomcat.apache.org%3E
- https://lists.apache.org/thread.html/eb6efa8d59c45a7a9eff94c4b925467d3b3fec8ba7697f3daa314b04@%3Cdev.tomcat.apache.org%3E
- https://lists.apache.org/thread.html/eb6efa8d59c45a7a9eff94c4b925467d3b3fec8ba7697f3daa314b04%40%3Cdev.tomcat.apache.org%3E
- https://lists.apache.org/thread.html/r6ccee4e849bc77df0840c7f853f6bd09d426f6741247da2b7429d5d9@%3Cdev.tomcat.apache.org%3E
- https://lists.apache.org/thread.html/r9136ff5b13e4f1941360b5a309efee2c114a14855578c3a2cbe5d19c%40%3Cdev.tomcat.apache.org%3E
