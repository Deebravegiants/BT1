# [H] Inconsistent Interpretation of HTTP Requests in Red Hat JBoss EAP

## Summary
Severity: High
Advisory: GHSA-57q5-x8jf-g7h8
CVE: CVE-2017-7561
CWE: CWE-444
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-57q5-x8jf-g7h8
Type: github-advisory

## Affected
- Maven: `org.jboss.resteasy:resteasy-jaxrs` — affected >=3.0.7.Final <3.0.25.Final
- Maven: `org.jboss.resteasy:resteasy-jaxrs` — affected >=3.1.4.Final <3.5.0.CR1

## Details
Red Hat JBoss EAP version 3.0.7.Final until 3.0.25.Final, 3.5.0.CR1, and 4.0.0.Beta1 is vulnerable to a server-side cache poisoning or CORS requests in the JAX-RS component resulting in a moderate impact.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-7561
- https://access.redhat.com/errata/RHSA-2018:0002
- https://access.redhat.com/errata/RHSA-2018:0003
- https://access.redhat.com/errata/RHSA-2018:0004
- https://access.redhat.com/errata/RHSA-2018:0005
- https://access.redhat.com/errata/RHSA-2018:0478
- https://access.redhat.com/errata/RHSA-2018:0479
- https://access.redhat.com/errata/RHSA-2018:0480
- https://access.redhat.com/errata/RHSA-2018:0481
- https://github.com/resteasy/Resteasy
- https://issues.jboss.org/browse/RESTEASY-1704
