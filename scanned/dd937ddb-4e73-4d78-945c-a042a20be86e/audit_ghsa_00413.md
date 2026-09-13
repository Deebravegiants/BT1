# [M] Apache Tomcat Race Condition vulnerability

## Summary
Severity: Medium
Advisory: GHSA-6v52-mj5r-7j2m
CVE: CVE-2018-8037
CWE: CWE-362
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2018-10-17
Source: https://github.com/advisories/GHSA-6v52-mj5r-7j2m
Type: github-advisory

## Affected
- Maven: `org.apache.tomcat.embed:tomcat-embed-core` — affected >=9.0.0.M9 <9.0.10
- Maven: `org.apache.tomcat.embed:tomcat-embed-core` — affected >=8.5.5 <8.5.32

## Details
If an async request was completed by the application at the same time as the container triggered the async timeout, a race condition existed that could result in a user seeing a response intended for a different user. An additional issue was present in the NIO and NIO2 connectors that did not correctly track the closure of the connection when an async request was completed by the application and timed out by the container at the same time. This could also result in a user seeing a response intended for another user. Versions Affected: Apache Tomcat 9.0.0.M9 to 9.0.9 and 8.5.5 to 8.5.31.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-8037
- https://github.com/apache/tomcat/commit/4c04369c287233ea2e8e5135f6c31d02e2d76293
- https://github.com/apache/tomcat/commit/ccf2e6bf5205561ad18c2300153e9173ec509d73
- https://github.com/apache/tomcat/commit/ed4b9d791f9470e4c3de691dd0153a9ce431701b
- https://github.com/apache/tomcat/commit/f94eedf02b5973598ab3dbbd4504da588e9ba6cb
- https://access.redhat.com/errata/RHSA-2018:2867
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
- https://lists.apache.org/thread.html/raba0fabaf4d56d4325ab2aca8814f0b30a237ab83d8106b115ee279a%40%3Cdev.tomcat.apache.org%3E
- https://lists.apache.org/thread.html/raba0fabaf4d56d4325ab2aca8814f0b30a237ab83d8106b115ee279a@%3Cdev.tomcat.apache.org%3E
- https://security.netapp.com/advisory/ntap-20180817-0001
- https://web.archive.org/web/20200227102808/http://www.securityfocus.com/bid/104894
