# [M] Denial of Service in org.springframework:spring-core

## Summary
Severity: Medium
Advisory: GHSA-rcpf-vj53-7h2m
CVE: CVE-2018-1257
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2018-10-17
Source: https://github.com/advisories/GHSA-rcpf-vj53-7h2m
Type: github-advisory

## Affected
- Maven: `org.springframework:spring-core` — affected >=5.0.0 <5.0.6
- Maven: `org.springframework:spring-core` — affected >=0 <4.3.17

## Details
Spring Framework, versions 5.0.x prior to 5.0.6, versions 4.3.x prior to 4.3.17, and older unsupported versions allows applications to expose STOMP over WebSocket endpoints with a simple, in-memory STOMP broker through the spring-messaging module. A malicious user (or attacker) can craft a message to the broker that can lead to a regular expression, denial of service attack.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-1257
- https://github.com/spring-projects/spring-framework/commit/246a6db1cad205ca9b6fca00c544ab7443ba202
- https://github.com/spring-projects/spring-framework/commit/ff2228fdaf131d57b5c8c5918ee8d07c6dd9bba
- https://access.redhat.com/errata/RHSA-2018:1809
- https://access.redhat.com/errata/RHSA-2018:3768
- https://github.com/advisories/GHSA-rcpf-vj53-7h2m
- https://github.com/spring-projects/spring-framework
- https://pivotal.io/security/cve-2018-1257
- https://www.oracle.com/security-alerts/cpujan2020.html
- https://www.oracle.com/security-alerts/cpujul2020.html
- https://www.oracle.com/security-alerts/cpuoct2021.html
- https://www.oracle.com/technetwork/security-advisory/cpuapr2019-5072813.html
- https://www.oracle.com/technetwork/security-advisory/cpujan2019-5072801.html
- https://www.oracle.com/technetwork/security-advisory/cpujul2019-5072835.html
- http://www.oracle.com/technetwork/security-advisory/cpuoct2018-4428296.html
- http://www.securityfocus.com/bid/104260
