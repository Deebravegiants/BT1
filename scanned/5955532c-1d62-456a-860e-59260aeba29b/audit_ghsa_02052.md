# [M] Cross-site scripting in RESTEasy

## Summary
Severity: Medium
Advisory: GHSA-29qj-rvv6-qrmv
CVE: CVE-2020-10688
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2021-06-15
Source: https://github.com/advisories/GHSA-29qj-rvv6-qrmv
Type: github-advisory

## Affected
- Maven: `org.jboss.resteasy:resteasy-bom` — affected >=0 <3.11.1.Final
- Maven: `org.jboss.resteasy:resteasy-bom` — affected >=4.0.0 <4.5.3.Final
- Maven: `org.jboss.resteasy:resteasy-core` — affected >=0 <3.11.1.Final
- Maven: `org.jboss.resteasy:resteasy-core` — affected >=4.0.0 <4.5.3.Final

## Details
A cross-site scripting (XSS) flaw was found in RESTEasy in versions before 3.11.1.Final and before 4.5.3.Final, where it did not properly handle URL encoding when the RESTEASY003870 exception occurs. An attacker could use this flaw to launch a reflected XSS attack.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-10688
- https://github.com/quarkusio/quarkus/issues/7248
- https://bugzilla.redhat.com/show_bug.cgi?id=1814974
- https://issues.redhat.com/browse/RESTEASY-2519
- https://security.netapp.com/advisory/ntap-20210706-0008
