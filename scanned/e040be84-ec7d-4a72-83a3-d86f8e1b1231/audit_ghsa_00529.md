# [M] Pivotal Spring Framework DoS Attack with XML Input

## Summary
Severity: Medium
Advisory: GHSA-6v7w-535j-rq5m
CVE: CVE-2015-3192
CWE: CWE-119
Ecosystem: Maven
CVSS: CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2018-10-17
Source: https://github.com/advisories/GHSA-6v7w-535j-rq5m
Type: github-advisory

## Affected
- Maven: `org.springframework:spring-web` — affected >=0 <3.2.14
- Maven: `org.springframework:spring-web` — affected >=4.0.0 <4.1.7
- Maven: `org.springframework:spring-web` — affected >=5.0.0.RC2 <5.0.0.RC3

## Details
Pivotal Spring Framework before 3.2.14 and 4.x before 4.1.7 do not properly process inline DTD declarations when DTD is not entirely disabled, which allows remote attackers to cause a denial of service (memory consumption and out-of-memory errors) via a crafted XML file.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2015-3192
- https://github.com/spring-projects/spring-framework/issues/17727
- https://github.com/spring-projects/spring-framework/issues/20352
- https://github.com/spring-projects/spring-framework/commit/0411435bac835de88a80a64b3f67b1b89244e907
- https://github.com/spring-projects/spring-framework/commit/38b8262e1e2db9be9d2171d81547da5c65ba7e09
- https://github.com/spring-projects/spring-framework/commit/5a711c05ec750f069235597173084c2ee7962424
- https://github.com/spring-projects/spring-framework/commit/9c3580d04e84d25a90ef4c249baee1b4e02df15e
- https://github.com/spring-projects/spring-framework/commit/d79ec68db40c381b8e205af52748ebd3163ee33b
- https://github.com/spring-projects/spring-framework/commit/e4651d6b50c5bc85c84ff537859c212ac4e33434
- https://spring.io/security/cve-2015-3192
- https://lists.debian.org/debian-lts-announce/2019/07/msg00012.html
- https://jira.spring.io/browse/SPR-13136?redirect=false
- https://jira.spring.io/browse/SPR-13136
- https://github.com/spring-projects/spring-framework
- https://github.com/advisories/GHSA-6v7w-535j-rq5m
- https://access.redhat.com/errata/RHSA-2016:1219
- https://access.redhat.com/errata/RHSA-2016:1218
- http://lists.fedoraproject.org/pipermail/package-announce/2015-July/162015.html
- http://lists.fedoraproject.org/pipermail/package-announce/2015-July/162017.html
- http://rhn.redhat.com/errata/RHSA-2016-1592.html
