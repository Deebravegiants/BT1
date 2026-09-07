# [M] WildFly Elytron OpenID Connect Client ExtensionOIDC authorization code injection attack

## Summary
Severity: Medium
Advisory: GHSA-5565-3c98-g6jc
CVE: CVE-2024-12369
CWE: CWE-345
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2025-03-25
Source: https://github.com/advisories/GHSA-5565-3c98-g6jc
Type: github-advisory

## Affected
- Maven: `org.wildfly.security:wildfly-elytron` — affected >=1.17.0.Final <2.2.9.Final
- Maven: `org.wildfly.security:wildfly-elytron` — affected >=2.3.0.Final <2.6.2.Final
- Maven: `org.wildfly.security:wildfly-elytron-http-oidc` — affected >=1.17.0.Final <2.2.9.Final
- Maven: `org.wildfly.security:wildfly-elytron-http-oidc` — affected >=2.3.0.Final <2.6.2.Final

## Details
### Impact

A vulnerability was found in OIDC-Client. When using the elytron-oidc-client subsystem with WildFly, authorization code injection attacks can occur, allowing an attacker to inject a stolen authorization code into the attacker's own session with the client with a victim's identity. This is usually done with a Man-in-the-Middle (MitM) or phishing attack.

### Patches

[2.2.9.Final](https://github.com/wildfly-security/wildfly-elytron/releases/tag/2.2.9.Final)
[2.6.2.Final](https://github.com/wildfly-security/wildfly-elytron/releases/tag/2.6.2.Final)

### Workarounds

Currently, no mitigation is currently available for this vulnerability.

### References

https://nvd.nist.gov/vuln/detail/CVE-2024-12369
https://access.redhat.com/security/cve/CVE-2024-12369	
https://bugzilla.redhat.com/show_bug.cgi?id=2331178
https://issues.redhat.com/browse/ELY-2887

## References
- https://github.com/wildfly-security/wildfly-elytron/security/advisories/GHSA-5565-3c98-g6jc
- https://nvd.nist.gov/vuln/detail/CVE-2024-12369
- https://github.com/wildfly-security/wildfly-elytron/pull/2253
- https://github.com/wildfly-security/wildfly-elytron/pull/2261
- https://github.com/wildfly-security/wildfly-elytron/commit/5ac5e6bbcba58883b3cebb2ddbcec4de140c5ceb
- https://github.com/wildfly-security/wildfly-elytron/commit/d7754f5a6a91ceb0f4dbbbfe301991f6a55404cb
- https://access.redhat.com/security/cve/CVE-2024-12369
- https://bugzilla.redhat.com/show_bug.cgi?id=2331178
- https://github.com/wildfly-security/wildfly-elytron
- https://issues.redhat.com/browse/ELY-2887
