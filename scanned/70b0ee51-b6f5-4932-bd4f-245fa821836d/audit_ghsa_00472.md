# [H] Possible privilege escalation in org.springframework:spring-core

## Summary
Severity: High
Advisory: GHSA-4487-x383-qpph
CVE: CVE-2018-1272
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2018-10-17
Source: https://github.com/advisories/GHSA-4487-x383-qpph
Type: github-advisory

## Affected
- Maven: `org.springframework:spring-core` — affected >=0 <4.3.15
- Maven: `org.springframework:spring-core` — affected >=5.0.0 <5.0.5

## Details
Spring Framework, versions 5.0 prior to 5.0.5 and versions 4.3 prior to 4.3.15 and older unsupported versions, provide client-side support for multipart requests. When Spring MVC or Spring WebFlux server application (server A) receives input from a remote client, and then uses that input to make a multipart request to another server (server B), it can be exposed to an attack, where an extra multipart is inserted in the content of the request from server A, causing server B to use the wrong value for a part it expects. This could to lead privilege escalation, for example, if the part content represents a username or user roles.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-1272
- https://github.com/spring-projects/spring-framework/commit/ab2410c754b67902f002bfcc0c3895bd7772d39
- https://github.com/spring-projects/spring-framework/commit/e02ff3a0da50744b0980d5d665fd242eedea767
- https://access.redhat.com/errata/RHSA-2018:1320
- https://access.redhat.com/errata/RHSA-2018:2669
- https://github.com/advisories/GHSA-4487-x383-qpph
- https://pivotal.io/security/cve-2018-1272
- https://www.oracle.com/security-alerts/cpujul2020.html
- https://www.oracle.com/security-alerts/cpuoct2021.html
- https://www.oracle.com/technetwork/security-advisory/cpujan2019-5072801.html
- https://www.oracle.com/technetwork/security-advisory/cpujul2019-5072835.html
- http://www.oracle.com/technetwork/security-advisory/cpujul2018-4258247.html
- http://www.oracle.com/technetwork/security-advisory/cpuoct2018-4428296.html
- http://www.securityfocus.com/bid/103697
