# [M] Apache Tomcat Reveals Path through Long URL

## Summary
Severity: Medium
Advisory: GHSA-2w2w-cv3h-rr38
CVE: CVE-2001-0917
CWE: CWE-200
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:L/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2022-04-30
Source: https://github.com/advisories/GHSA-2w2w-cv3h-rr38
Type: github-advisory

## Affected
- Maven: `org.apache.tomcat:tomcat` — affected >=0 <4.0.2

## Details
Jakarta Tomcat 4.0.1 allows remote attackers to reveal physical path information by requesting a long URL with a .JSP extension.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2001-0917
- https://exchange.xforce.ibmcloud.com/vulnerabilities/7599
- https://github.com/apache/tomcat
- https://lists.apache.org/thread.html/29dc6c2b625789e70a9c4756b5a327e6547273ff8bde7e0327af48c5%40%3Cdev.tomcat.apache.org%3E
- https://lists.apache.org/thread.html/29dc6c2b625789e70a9c4756b5a327e6547273ff8bde7e0327af48c5@%3Cdev.tomcat.apache.org%3E
- https://lists.apache.org/thread.html/c62b0e3a7bf23342352a5810c640a94b6db69957c5c19db507004d74%40%3Cdev.tomcat.apache.org%3E
- https://lists.apache.org/thread.html/c62b0e3a7bf23342352a5810c640a94b6db69957c5c19db507004d74@%3Cdev.tomcat.apache.org%3E
- https://lists.apache.org/thread.html/rb71997f506c6cc8b530dd845c084995a9878098846c7b4eacfae8db3%40%3Cdev.tomcat.apache.org%3E
- https://lists.apache.org/thread.html/rb71997f506c6cc8b530dd845c084995a9878098846c7b4eacfae8db3@%3Cdev.tomcat.apache.org%3E
- http://marc.info/?l=bugtraq&m=100654722925155&w=2
- http://marc.info/?l=tomcat-dev&m=100658457507305&w=2
