# [H] Keycloak mTLS Authentication Bypass via Reverse Proxy TLS Termination 

## Summary
Severity: High
Advisory: GHSA-93ww-43rr-79v3
CVE: CVE-2024-10039
CWE: CWE-295
Ecosystem: Maven
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2024-11-25
Source: https://github.com/advisories/GHSA-93ww-43rr-79v3
Type: github-advisory

## Affected
- Maven: `org.keycloak:keycloak-core` — affected >=0 <26.0.6

## Details
A vulnerability was found in Keycloak. Deployments of Keycloak with a reverse proxy not using pass-through termination of TLS, with mTLS enabled, are affected. This issue may allow an attacker on the local network to authenticate as any user or client that leverages mTLS as the authentication mechanism.

## References
- https://github.com/keycloak/keycloak/security/advisories/GHSA-93ww-43rr-79v3
- https://github.com/keycloak/keycloak/issues/35217
- https://github.com/keycloak/keycloak
