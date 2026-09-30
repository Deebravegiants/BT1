# [M] JacksonJsonpInterceptor susceptible to cross-site script inclusion (XSSI) attack

## Summary
Severity: Medium
Advisory: GHSA-9xfc-j5mf-9w5p
CVE: CVE-2016-6348
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-9xfc-j5mf-9w5p
Type: github-advisory

## Affected
- Maven: `org.jboss.resteasy:resteasy-client` — affected >=0 <3.0.20.Final

## Details
JacksonJsonpInterceptor in RESTEasy might allow remote attackers to conduct a cross-site script inclusion (XSSI) attack.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-6348
- https://bugzilla.redhat.com/show_bug.cgi?id=1372129
- https://github.com/resteasy/Resteasy
