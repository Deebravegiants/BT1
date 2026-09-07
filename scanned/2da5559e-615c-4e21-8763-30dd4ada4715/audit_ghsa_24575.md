# [M] Cross-Site Request Forgery in Spring Framework

## Summary
Severity: Medium
Advisory: GHSA-rp4p-g69r-438x
CVE: CVE-2013-4152
CWE: CWE-352
Ecosystem: Maven
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-rp4p-g69r-438x
Type: github-advisory

## Affected
- Maven: `org.springframework:spring-oxm` — affected >=0 <3.2.4.RELEASE

## Details
The Spring OXM wrapper in Spring Framework before 3.2.4 and 4.0.0.M1, when using the JAXB marshaller, does not disable entity resolution, which allows context-dependent attackers to read arbitrary files, cause a denial of service, and conduct CSRF attacks via an XML external entity declaration in conjunction with an entity reference in a (1) DOMSource, (2) StAXSource, (3) SAXSource, or (4) StreamSource, aka an XML External Entity (XXE) issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2013-4152
- https://github.com/spring-projects/spring-framework/pull/317/files
- https://github.com/spring-projects/spring-framework/commit/434735fbf6e7f9051af2ef027657edb99120b173
- https://github.com/spring-projects/spring-framework/commit/7576274874deeccb6da6b09a8d5bd62e8b5538b7
- http://rhn.redhat.com/errata/RHSA-2014-0212.html
- http://rhn.redhat.com/errata/RHSA-2014-0245.html
- http://rhn.redhat.com/errata/RHSA-2014-0254.html
- http://rhn.redhat.com/errata/RHSA-2014-0400.html
- http://seclists.org/bugtraq/2013/Aug/154
- http://seclists.org/fulldisclosure/2013/Nov/14
- http://www.debian.org/security/2014/dsa-2842
- http://www.gopivotal.com/security/cve-2013-4152
