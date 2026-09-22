# [H] spring-security-oauth2-client vulnerable to Privilege Escalation

## Summary
Severity: High
Advisory: GHSA-32vj-v39g-jh23
CVE: CVE-2022-31690
CWE: CWE-269
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-11-01
Source: https://github.com/advisories/GHSA-32vj-v39g-jh23
Type: github-advisory

## Affected
- Maven: `org.springframework.security:spring-security-oauth2-client` — affected >=5.7.0 <5.7.5
- Maven: `org.springframework.security:spring-security-oauth2-client` — affected >=0 <5.6.9

## Details
Spring Security, versions 5.7 prior to 5.7.5, and 5.6 prior to 5.6.9, and older unsupported versions could be susceptible to a privilege escalation under certain conditions. A malicious user or attacker can modify a request initiated by the Client (via the browser) to the Authorization Server which can lead to a privilege escalation on the subsequent approval. This scenario can happen if the Authorization Server responds with an OAuth2 Access Token Response containing an empty scope list (per RFC 6749, Section 5.1) on the subsequent request to the token endpoint to obtain the access token.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-31690
- https://github.com/spring-projects/spring-security-samples/blob/4638e1e428ee2ddab234199eb3b67b9c94dfa08b/servlet/spring-boot/java/oauth2/webclient/src/main/java/example/SecurityConfiguration.java#L48
- https://security.netapp.com/advisory/ntap-20221215-0010
- https://tanzu.vmware.com/security/cve-2022-31690
