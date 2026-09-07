# [M] Missing XML Validation in Spring Framework

## Summary
Severity: Medium
Advisory: GHSA-vp63-rrcm-9mph
CVE: CVE-2013-7315
CWE: CWE-112
Ecosystem: Maven
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-vp63-rrcm-9mph
Type: github-advisory

## Affected
- Maven: `org.springframework:spring-oxm` — affected >=0 <3.2.4.RELEASE

## Details
The Spring MVC in Spring Framework before 3.2.4 and 4.0.0.M1 through 4.0.0.M2 does not disable external entity resolution for the StAX XMLInputFactory, which allows context-dependent attackers to read arbitrary files, cause a denial of service, and conduct CSRF attacks via crafted XML with JAXB, aka an XML External Entity (XXE) issue, and a different vulnerability than CVE-2013-4152.  NOTE: this issue was SPLIT from CVE-2013-4152 due to different affected versions.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2013-7315
- https://github.com/spring-projects/spring-framework/issues/15432
- https://github.com/spring-projects/spring-framework/commit/434735fbf6e7f9051af2ef027657edb99120b173
- https://github.com/spring-projects/spring-framework/commit/7576274874deeccb6da6b09a8d5bd62e8b5538b7
- https://jira.spring.io/browse/SPR-10806?redirect=false
- http://seclists.org/bugtraq/2013/Aug/154
- http://seclists.org/fulldisclosure/2013/Nov/14
- http://www.debian.org/security/2014/dsa-2842
- http://www.securityfocus.com/bid/77998
