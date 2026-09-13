# [M] Spring Web Services: Inbound WS-Security allows RSA PKCS#1 v1.5 key transport by default

## Summary
Severity: Medium
Advisory: GHSA-p7qj-2q5w-f9r7
CVE: CVE-2026-40996
CWE: CWE-327
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2026-06-11
Source: https://github.com/advisories/GHSA-p7qj-2q5w-f9r7
Type: github-advisory

## Affected
- Maven: `org.springframework.ws:spring-ws-security` — affected >=5.0.0 <5.0.2
- Maven: `org.springframework.ws:spring-ws-security` — affected >=4.1.0 <4.1.4
- Maven: `org.springframework.ws:spring-ws-security` — affected >=4.0.0
- Maven: `org.springframework.ws:spring-ws-security` — affected >=3.1.0

## Details
Wss4jSecurityInterceptor defaulted allowRSA15KeyTransportAlgorithm to true, overriding Apache WSS4J's safer default for validation RequestData. Inbound WS-Security decryption could therefore accept RSA PKCS#1 v1.5 (rsa-1_5) encrypted key material unless operators explicitly reconfigured the flag.

Affected versions:
Spring Web Services 5.0.0 through 5.0.1; 4.1.0 through 4.1.3; 4.0.0 through 4.0.18; 3.1.0 through 3.1.8.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-40996
- https://github.com/spring-projects/spring-ws
- https://spring.io/security/cve-2026-40996
