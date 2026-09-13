# [M] Apache Tomcat Reveals Directories

## Summary
Severity: Medium
Advisory: GHSA-wfj7-mhr5-pcwq
CVE: CVE-2006-3835
CWE: CWE-200
Ecosystem: Maven
Published: 2022-05-01
Source: https://github.com/advisories/GHSA-wfj7-mhr5-pcwq
Type: github-advisory

## Affected
- Maven: `org.apache.tomcat:tomcat` — affected >=5.0.0 <5.5.17

## Details
Apache Tomcat 5 before 5.5.17 allows remote attackers to list directories via a semicolon (`;`) preceding a filename with a mapped extension, as demonstrated by URLs ending with `/;index.jsp` and `/;help.do`.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2006-3835
- https://exchange.xforce.ibmcloud.com/vulnerabilities/27902
- https://exchange.xforce.ibmcloud.com/vulnerabilities/34183
- https://github.com/apache/tomcat
- https://lists.apache.org/thread.html/29dc6c2b625789e70a9c4756b5a327e6547273ff8bde7e0327af48c5%40%3Cdev.tomcat.apache.org%3E
- https://lists.apache.org/thread.html/29dc6c2b625789e70a9c4756b5a327e6547273ff8bde7e0327af48c5@%3Cdev.tomcat.apache.org%3E
- https://lists.apache.org/thread.html/c62b0e3a7bf23342352a5810c640a94b6db69957c5c19db507004d74%40%3Cdev.tomcat.apache.org%3E
- https://lists.apache.org/thread.html/c62b0e3a7bf23342352a5810c640a94b6db69957c5c19db507004d74@%3Cdev.tomcat.apache.org%3E
- https://lists.apache.org/thread.html/rb71997f506c6cc8b530dd845c084995a9878098846c7b4eacfae8db3%40%3Cdev.tomcat.apache.org%3E
- https://lists.apache.org/thread.html/rb71997f506c6cc8b530dd845c084995a9878098846c7b4eacfae8db3@%3Cdev.tomcat.apache.org%3E
- https://web.archive.org/web/20200517122628/http://www.securityfocus.com/archive/1/500396/100/0/threaded
- https://web.archive.org/web/20200517153851/http://www.securityfocus.com/archive/1/500412/100/0/threaded
- https://web.archive.org/web/20200525234537/http://securitytracker.com/id?1016576
- https://web.archive.org/web/20200526144006/http://www.securityfocus.com/archive/1/507729/100/0/threaded
- https://web.archive.org/web/20200526152646/http://www.securityfocus.com/archive/1/468048/100/0/threaded
- https://web.archive.org/web/20200526165235/http://www.securityfocus.com/bid/19106
- http://archives.neohapsis.com/archives/fulldisclosure/2006-07/0467.html
- http://community.ca.com/blogs/casecurityresponseblog/archive/2009/01/23.aspx
- http://lists.opensuse.org/opensuse-security-announce/2009-02/msg00002.html
- http://sunsolve.sun.com/search/document.do?assetkey=1-26-239312-1
