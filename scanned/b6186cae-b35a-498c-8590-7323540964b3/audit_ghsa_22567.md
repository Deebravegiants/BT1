# [M] Apache Tomcat Directory Traversal

## Summary
Severity: Medium
Advisory: GHSA-4prh-gqw8-rgh5
CVE: CVE-2007-0450
CWE: CWE-22
Ecosystem: Maven
Published: 2022-05-01
Source: https://github.com/advisories/GHSA-4prh-gqw8-rgh5
Type: github-advisory

## Affected
- Maven: `org.apache.tomcat:tomcat` — affected >=5.0 <5.5.22
- Maven: `org.apache.tomcat:tomcat` — affected >=6.0 <6.0.10

## Details
Directory traversal vulnerability in Tomcat 5.x before 5.5.22 and 6.x before 6.0.10, when using certain proxy modules (mod_proxy, mod_rewrite, mod_jk), allows remote attackers to read arbitrary files via a `..` (dot dot) sequence with combinations of (1) `/` (slash), (2) `\` (backslash), and (3) URL-encoded backslash (`%5C`) characters in the URL, which are valid separators in Tomcat but not in Apache.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2007-0450
- https://github.com/apache/tomcat/commit/0c5ec5b958f1b59840ee155a23ab409755b039f6
- https://github.com/apache/tomcat/commit/19ec1ccd17fbb98511bc1c12b255253c4f48b85f
- https://github.com/apache/tomcat/commit/ec7ff880dbc28b313bf3a2b1914f6f0371489793
- https://lists.apache.org/thread.html/rf8e8c091182b45daa50d3557cad9b10bb4198e3f08cf8f1c66a1b08d@%3Cdev.tomcat.apache.org%3E
- https://lists.apache.org/thread.html/rf8e8c091182b45daa50d3557cad9b10bb4198e3f08cf8f1c66a1b08d%40%3Cdev.tomcat.apache.org%3E
- https://lists.apache.org/thread.html/rb71997f506c6cc8b530dd845c084995a9878098846c7b4eacfae8db3@%3Cdev.tomcat.apache.org%3E
- https://lists.apache.org/thread.html/rb71997f506c6cc8b530dd845c084995a9878098846c7b4eacfae8db3%40%3Cdev.tomcat.apache.org%3E
- https://lists.apache.org/thread.html/r5c616dfc49156e4b06ffab842800c80f4425924d0f20c452c127a53c@%3Cdev.tomcat.apache.org%3E
- https://lists.apache.org/thread.html/r5c616dfc49156e4b06ffab842800c80f4425924d0f20c452c127a53c%40%3Cdev.tomcat.apache.org%3E
- https://lists.apache.org/thread.html/c62b0e3a7bf23342352a5810c640a94b6db69957c5c19db507004d74@%3Cdev.tomcat.apache.org%3E
- https://lists.apache.org/thread.html/c62b0e3a7bf23342352a5810c640a94b6db69957c5c19db507004d74%40%3Cdev.tomcat.apache.org%3E
- https://lists.apache.org/thread.html/ba661b0edd913b39ff129a32d855620dd861883ade05fd88a8ce517d@%3Cdev.tomcat.apache.org%3E
- https://lists.apache.org/thread.html/ba661b0edd913b39ff129a32d855620dd861883ade05fd88a8ce517d%40%3Cdev.tomcat.apache.org%3E
- https://lists.apache.org/thread.html/8d2a579bbd977c225c70cb23b0ec54865fb0dab5da3eff1e060c9935@%3Cdev.tomcat.apache.org%3E
- https://lists.apache.org/thread.html/8d2a579bbd977c225c70cb23b0ec54865fb0dab5da3eff1e060c9935%40%3Cdev.tomcat.apache.org%3E
- https://lists.apache.org/thread.html/5b7a23e245c93235c503900da854a143596d901bf1a1f67e851a5de4@%3Cdev.tomcat.apache.org%3E
- https://lists.apache.org/thread.html/5b7a23e245c93235c503900da854a143596d901bf1a1f67e851a5de4%40%3Cdev.tomcat.apache.org%3E
- https://lists.apache.org/thread.html/29dc6c2b625789e70a9c4756b5a327e6547273ff8bde7e0327af48c5@%3Cdev.tomcat.apache.org%3E
- https://lists.apache.org/thread.html/29dc6c2b625789e70a9c4756b5a327e6547273ff8bde7e0327af48c5%40%3Cdev.tomcat.apache.org%3E
