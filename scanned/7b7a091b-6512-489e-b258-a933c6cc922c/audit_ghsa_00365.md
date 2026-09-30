# [C] The defaults settings for the CORS filter provided in Apache Tomcat are insecure and enable 'supportsCredentials' for all origins

## Summary
Severity: Critical
Advisory: GHSA-r4x2-3cq5-hqvp
CVE: CVE-2018-8014
CWE: CWE-1188
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2018-10-17
Source: https://github.com/advisories/GHSA-r4x2-3cq5-hqvp
Type: github-advisory

## Affected
- Maven: `org.apache.tomcat.embed:tomcat-embed-core` — affected >=9.0.0.M1 <9.0.9
- Maven: `org.apache.tomcat.embed:tomcat-embed-core` — affected >=8.5.0 <8.5.32
- Maven: `org.apache.tomcat.embed:tomcat-embed-core` — affected >=8.0.0RC1 <8.0.53
- Maven: `org.apache.tomcat.embed:tomcat-embed-core` — affected >=7.0.41 <7.0.88

## Details
The defaults settings for the CORS filter provided in Apache Tomcat 9.0.0.M1 to 9.0.8, 8.5.0 to 8.5.31, 8.0.0.RC1 to 8.0.52, 7.0.41 to 7.0.88 are insecure and enable 'supportsCredentials' for all origins. It is expected that users of the CORS filter will have configured it appropriately for their environment rather than using it in the default configuration. Therefore, it is expected that most users will not be impacted by this issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-8014
- https://github.com/apache/tomcat80/commit/2c9d8433bd3247a2856d4b2555447108758e813e
- https://github.com/apache/tomcat/commit/d83a76732e6804739b81d8b2056365307637b42d
- https://github.com/apache/tomcat/commit/5877390a9605f56d9bd6859a54ccbfb16374a78b
- https://github.com/apache/tomcat/commit/60f596a21fd6041335a3a1a4015d4512439cecb5
- https://lists.apache.org/thread.html/r9136ff5b13e4f1941360b5a309efee2c114a14855578c3a2cbe5d19c%40%3Cdev.tomcat.apache.org%3E
- https://lists.apache.org/thread.html/r6ccee4e849bc77df0840c7f853f6bd09d426f6741247da2b7429d5d9@%3Cdev.tomcat.apache.org%3E
- https://lists.apache.org/thread.html/r6ccee4e849bc77df0840c7f853f6bd09d426f6741247da2b7429d5d9%40%3Cdev.tomcat.apache.org%3E
- https://lists.apache.org/thread.html/r48c1444845fe15a823e1374674bfc297d5008a5453788099ea14caf0@%3Cdev.tomcat.apache.org%3E
- https://lists.apache.org/thread.html/r48c1444845fe15a823e1374674bfc297d5008a5453788099ea14caf0%40%3Cdev.tomcat.apache.org%3E
- https://lists.apache.org/thread.html/r3bbb800a816d0a51eccc5a228c58736960a9fffafa581a225834d97d@%3Cdev.tomcat.apache.org%3E
- https://lists.apache.org/thread.html/r3bbb800a816d0a51eccc5a228c58736960a9fffafa581a225834d97d%40%3Cdev.tomcat.apache.org%3E
- https://lists.apache.org/thread.html/fbfb713e4f8a4c0f81089b89450828011343593800cae3fb629192b1@%3Cannounce.tomcat.apache.org%3E
- https://lists.apache.org/thread.html/fbfb713e4f8a4c0f81089b89450828011343593800cae3fb629192b1%40%3Cannounce.tomcat.apache.org%3E
- https://lists.apache.org/thread.html/eb6efa8d59c45a7a9eff94c4b925467d3b3fec8ba7697f3daa314b04@%3Cdev.tomcat.apache.org%3E
- https://lists.apache.org/thread.html/eb6efa8d59c45a7a9eff94c4b925467d3b3fec8ba7697f3daa314b04%40%3Cdev.tomcat.apache.org%3E
- https://lists.apache.org/thread.html/e85e83e9954f169bbb77b44baae5a33d8de878df557bb32b7f793661@%3Cdev.tomcat.apache.org%3E
- https://lists.apache.org/thread.html/e85e83e9954f169bbb77b44baae5a33d8de878df557bb32b7f793661%40%3Cdev.tomcat.apache.org%3E
- https://lists.apache.org/thread.html/b5e3f51d28cd5d9b1809f56594f2cf63dcd6a90429e16ea9f83bbedc@%3Cdev.tomcat.apache.org%3E
- https://lists.apache.org/thread.html/r9136ff5b13e4f1941360b5a309efee2c114a14855578c3a2cbe5d19c@%3Cdev.tomcat.apache.org%3E
