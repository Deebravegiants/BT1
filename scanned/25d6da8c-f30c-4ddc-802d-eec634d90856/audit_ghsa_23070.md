# [M] Apache Tomcat Unrestricted file upload vulnerability

## Summary
Severity: Medium
Advisory: GHSA-h6c8-x5r3-pm88
CVE: CVE-2013-4444
CWE: CWE-94
Ecosystem: Maven
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-h6c8-x5r3-pm88
Type: github-advisory

## Affected
- Maven: `org.apache.tomcat:tomcat` — affected >=7.0 <7.0.40

## Details
Unrestricted file upload vulnerability in Apache Tomcat 7.x before 7.0.40, in certain situations involving outdated java.io.File code and a custom JMX configuration, allows remote attackers to execute arbitrary code by uploading and accessing a JSP file.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2013-4444
- https://github.com/apache/tomcat
- https://h20564.www2.hpe.com/portal/site/hpsc/public/kb/docDisplay?docId=emr_na-c04851013
- http://archives.neohapsis.com/archives/bugtraq/2014-09/0075.html
- http://marc.info/?l=bugtraq&m=144498216801440&w=2
- http://openwall.com/lists/oss-security/2014/10/24/12
- http://seclists.org/fulldisclosure/2021/Jan/23
- http://tomcat.apache.org/security-7.html
- http://www.debian.org/security/2016/dsa-3447
- http://www.oracle.com/technetwork/security-advisory/cpuoct2016-2881722.html
- http://www.securityfocus.com/bid/69728
- http://www.securitytracker.com/id/1030834
