# [C] SimpleXML has XML External Entity (XXE) vulnerability

## Summary
Severity: Critical
Advisory: GHSA-f5qf-vh69-9q4r
CVE: CVE-2017-1000190
CWE: CWE-611
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-f5qf-vh69-9q4r
Type: github-advisory

## Affected
- Maven: `org.simpleframework:simple-xml` — affected >=0 <2.7.1

## Details
SimpleXML (latest version 2.7.1) is vulnerable to an XXE vulnerability resulting SSRF, information disclosure, DoS and so on.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-1000190
- https://github.com/ngallagher/simplexml/issues/18
- https://github.com/ngallagher/simplexml
- https://lists.apache.org/thread.html/708d94141126eac03011144a971a6411fcac16d9c248d1d535a39451%40%3Csolr-user.lucene.apache.org%3E
- https://lists.apache.org/thread.html/708d94141126eac03011144a971a6411fcac16d9c248d1d535a39451@%3Csolr-user.lucene.apache.org%3E
- https://lists.apache.org/thread.html/8c4ef27e2c0218f29e785990dc919266855aea137c958f10d242cb36%40%3Cdev.lucene.apache.org%3E
- https://lists.apache.org/thread.html/8c4ef27e2c0218f29e785990dc919266855aea137c958f10d242cb36@%3Cdev.lucene.apache.org%3E
- https://lists.apache.org/thread.html/r204ba2a9ea750f38d789d2bb429cc0925ad6133deea7cbc3001d96b5%40%3Csolr-user.lucene.apache.org%3E
- https://lists.apache.org/thread.html/r204ba2a9ea750f38d789d2bb429cc0925ad6133deea7cbc3001d96b5@%3Csolr-user.lucene.apache.org%3E
