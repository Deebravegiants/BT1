# [H] Resource Exhaustion in Spring Security

## Summary
Severity: High
Advisory: GHSA-w9jg-gvgr-354m
CVE: CVE-2021-22119
CWE: CWE-400, CWE-863
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2021-07-02
Source: https://github.com/advisories/GHSA-w9jg-gvgr-354m
Type: github-advisory

## Affected
- Maven: `org.springframework.security:spring-security-core` — affected >=5.5.0 <5.5.1
- Maven: `org.springframework.security:spring-security-core` — affected >=5.4.0 <5.4.7
- Maven: `org.springframework.security:spring-security-core` — affected >=5.3.0 <5.3.10
- Maven: `org.springframework.security:spring-security-core` — affected >=5.2.0 <5.2.11
- Maven: `org.springframework.security:spring-security-oauth2-client` — affected >=5.5.0 <5.5.1
- Maven: `org.springframework.security:spring-security-oauth2-client` — affected >=5.4.0 <5.4.7
- Maven: `org.springframework.security:spring-security-oauth2-client` — affected >=5.3.0 <5.3.10
- Maven: `org.springframework.security:spring-security-oauth2-client` — affected >=5.2.0 <5.2.11

## Details
Spring Security versions 5.5.x prior to 5.5.1, 5.4.x prior to 5.4.7, 5.3.x prior to 5.3.10 and 5.2.x prior to 5.2.11 are susceptible to a Denial-of-Service (DoS) attack via the initiation of the Authorization Request in an OAuth 2.0 Client Web and WebFlux application. A malicious user or attacker can send multiple requests initiating the Authorization Request for the Authorization Code Grant, which has the potential of exhausting system resources using a single session or multiple sessions.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-22119
- https://github.com/spring-projects/spring-security/pull/9513
- https://github.com/spring-projects/spring-security
- https://lists.apache.org/thread.html/r08a449010786e0bcffa4b5781b04fcb55d6eafa62cb79b8347680aad@%3Cissues.nifi.apache.org%3E
- https://lists.apache.org/thread.html/r163b3e4e39803882f5be05ee8606b2b9812920e196daa2a82997ce14@%3Cpluto-dev.portals.apache.org%3E
- https://lists.apache.org/thread.html/r3868207b967f926819fe3aa8d33f1666429be589bb4a62104a49f4e3@%3Cpluto-dev.portals.apache.org%3E
- https://lists.apache.org/thread.html/r390783b3b1c59b978131ac08390bf77fbb3863270cbde59d5b0f5fde@%3Cpluto-dev.portals.apache.org%3E
- https://lists.apache.org/thread.html/r89aa1b48a827f5641310305214547f1d6b2101971a49b624737c497f@%3Cpluto-dev.portals.apache.org%3E
- https://lists.apache.org/thread.html/ra53677224fe4f04c2599abc88032076faa18dc84b329cdeba85d4cfc@%3Cpluto-scm.portals.apache.org%3E
- https://tanzu.vmware.com/security/cve-2021-22119
- https://www.oracle.com/security-alerts/cpujan2022.html
- https://www.oracle.com/security-alerts/cpujul2022.html
