# [H] Apache Tomcat Denial of Service vulnerability

## Summary
Severity: High
Advisory: GHSA-qcxh-w3j9-58qr
CVE: CVE-2019-0199
CWE: CWE-400
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2020-06-15
Source: https://github.com/advisories/GHSA-qcxh-w3j9-58qr
Type: github-advisory

## Affected
- Maven: `org.apache.tomcat.embed:tomcat-embed-core` — affected >=9.0.0 <9.0.16
- Maven: `org.apache.tomcat.embed:tomcat-embed-core` — affected >=8.0.0 <8.5.38
- Maven: `org.apache.tomcat:tomcat-coyote` — affected >=9.0.0 <9.0.16
- Maven: `org.apache.tomcat:tomcat-coyote` — affected >=8.0.0 <8.5.38

## Details
The HTTP/2 implementation in Apache Tomcat 9.0.0.M1 to 9.0.14 and 8.5.0 to 8.5.37 accepted streams with excessive numbers of SETTINGS frames and also permitted clients to keep streams open without reading/writing request/response data. By keeping streams open for requests that utilised the Servlet API's blocking I/O, clients were able to cause server-side threads to block eventually leading to thread exhaustion and a DoS.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-0199
- https://lists.apache.org/thread.html/e1b0b273b6e8ddcc72c9023bc2394b1276fc72664144bf21d0a87995@%3Cannounce.tomcat.apache.org%3E
- https://lists.apache.org/thread.html/e56886e1bac9319ecce81b3612dd7a1a43174a3a741a1c805e16880e%40%3Ccommits.tomee.apache.org%3E
- https://lists.apache.org/thread.html/e56886e1bac9319ecce81b3612dd7a1a43174a3a741a1c805e16880e@%3Ccommits.tomee.apache.org%3E
- https://lists.apache.org/thread.html/e85e83e9954f169bbb77b44baae5a33d8de878df557bb32b7f793661%40%3Cdev.tomcat.apache.org%3E
- https://lists.apache.org/thread.html/e85e83e9954f169bbb77b44baae5a33d8de878df557bb32b7f793661@%3Cdev.tomcat.apache.org%3E
- https://lists.apache.org/thread.html/e87733036e8c84ea648cdcdca3098f3c8a897e2652c33062b2b1535c%40%3Cusers.tomcat.apache.org%3E
- https://lists.apache.org/thread.html/e87733036e8c84ea648cdcdca3098f3c8a897e2652c33062b2b1535c@%3Cusers.tomcat.apache.org%3E
- https://lists.apache.org/thread.html/r3bbb800a816d0a51eccc5a228c58736960a9fffafa581a225834d97d%40%3Cdev.tomcat.apache.org%3E
- https://lists.apache.org/thread.html/r3bbb800a816d0a51eccc5a228c58736960a9fffafa581a225834d97d@%3Cdev.tomcat.apache.org%3E
- https://lists.apache.org/thread.html/r48c1444845fe15a823e1374674bfc297d5008a5453788099ea14caf0%40%3Cdev.tomcat.apache.org%3E
- https://lists.apache.org/thread.html/r48c1444845fe15a823e1374674bfc297d5008a5453788099ea14caf0@%3Cdev.tomcat.apache.org%3E
- https://lists.apache.org/thread.html/r6ccee4e849bc77df0840c7f853f6bd09d426f6741247da2b7429d5d9%40%3Cdev.tomcat.apache.org%3E
- https://lists.apache.org/thread.html/r6ccee4e849bc77df0840c7f853f6bd09d426f6741247da2b7429d5d9@%3Cdev.tomcat.apache.org%3E
- https://lists.apache.org/thread.html/raba0fabaf4d56d4325ab2aca8814f0b30a237ab83d8106b115ee279a%40%3Cdev.tomcat.apache.org%3E
- https://lists.apache.org/thread.html/raba0fabaf4d56d4325ab2aca8814f0b30a237ab83d8106b115ee279a@%3Cdev.tomcat.apache.org%3E
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/NPHQEL5AQ6LZSZD2Y6TYZ4RC3WI7NXJ3
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/ZQTZ5BJ5F4KV6N53SGNKSW3UY5DBIQ46
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/NPHQEL5AQ6LZSZD2Y6TYZ4RC3WI7NXJ3
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/ZQTZ5BJ5F4KV6N53SGNKSW3UY5DBIQ46
