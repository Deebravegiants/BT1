# [M] Improper Control of Generation of Code ('Code Injection') in Spring Framework

## Summary
Severity: Medium
Advisory: GHSA-vpr3-f594-mg5g
CVE: CVE-2010-1622
CWE: CWE-94
Ecosystem: Maven
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-vpr3-f594-mg5g
Type: github-advisory

## Affected
- Maven: `org.springframework:spring` — affected >=2.5.0 <2.5.7
- Maven: `org.springframework:spring` — affected >=3.0.0 <3.0.3

## Details
SpringSource Spring Framework 2.5.x before 2.5.6.SEC02, 2.5.7 before 2.5.7.SR01, and 3.0.x before 3.0.3 allows remote attackers to execute arbitrary code via an HTTP request containing `class.classLoader.URLs[0]=jar:` followed by a URL of a crafted .jar file.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2010-1622
- https://github.com/spring-projects/spring-framework/commit/3a5af35d37c79d0644d49b93f792a4c18fe8eb71
- https://access.redhat.com/errata/RHSA-2011:0175
- https://access.redhat.com/security/cve/CVE-2010-1622
- https://bugzilla.redhat.com/show_bug.cgi?id=606706
- https://github.com/spring-projects/spring-framework
- https://seclists.org/fulldisclosure/2010/Jun/456
- https://web.archive.org/web/20100623011648/http://www.springsource.com/security/cve-2010-1622
- https://web.archive.org/web/20161014113129/http://www.securitytracker.com/id/1033898
- https://web.archive.org/web/20200227210033/http://www.securityfocus.com/archive/1/511877
- https://web.archive.org/web/20200228060816/http://www.securityfocus.com/bid/40954
- http://geronimo.apache.org/2010/07/21/apache-geronimo-v216-released.html
- http://geronimo.apache.org/21x-security-report.html
- http://geronimo.apache.org/22x-security-report.html
- http://www.exploit-db.com/exploits/13918
- http://www.oracle.com/technetwork/topics/security/cpuoct2015-2367953.html
- http://www.redhat.com/support/errata/RHSA-2011-0175.html
