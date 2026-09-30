# [C] Improper Input Validation in Spring AMQP

## Summary
Severity: Critical
Advisory: GHSA-hrp3-8p5w-27gv
CVE: CVE-2016-2173
CWE: CWE-20
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-hrp3-8p5w-27gv
Type: github-advisory

## Affected
- Maven: `org.springframework.amqp:spring-amqp` — affected >=0 <1.5.5

## Details
org.springframework.core.serializer.DefaultDeserializer in Spring AMQP before 1.5.5 allows remote attackers to execute arbitrary code.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-2173
- https://bugzilla.redhat.com/show_bug.cgi?id=1326205
- https://pivotal.io/security/cve-2016-2173
- http://lists.fedoraproject.org/pipermail/package-announce/2016-April/182551.html
- http://lists.fedoraproject.org/pipermail/package-announce/2016-April/182850.html
- http://lists.fedoraproject.org/pipermail/package-announce/2016-April/182959.html
