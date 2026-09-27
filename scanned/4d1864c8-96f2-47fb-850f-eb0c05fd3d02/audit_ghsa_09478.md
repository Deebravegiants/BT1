# [M] Keycloak: Unauthorized account takeover via WebAuthn token replay

## Summary
Severity: Medium
Advisory: GHSA-w4p5-rfh6-cwrv
CVE: CVE-2026-37982
CWE: CWE-294
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-05-19
Source: https://github.com/advisories/GHSA-w4p5-rfh6-cwrv
Type: github-advisory

## Affected
- Maven: `org.keycloak:keycloak-services` — affected >=0 <26.6.2

## Details
A flaw was found in Keycloak. This authentication vulnerability allows a remote attacker to replay `ExecuteActionsActionToken` tokens within Keycloak's WebAuthn (Web Authentication) flow. By intercepting an execute-actions email link, an attacker can register their own authenticator to a victim's account. This leads to unauthorized enrollment of a hardware-backed credential, enabling persistent account takeover.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-37982
- https://github.com/keycloak/keycloak/pull/49126
- https://github.com/keycloak/keycloak/commit/2d1a24f501454a44c52daa62855419b31dc499c1
- https://access.redhat.com/errata/RHSA-2026:19596
- https://access.redhat.com/errata/RHSA-2026:19597
- https://access.redhat.com/security/cve/CVE-2026-37982
- https://bugzilla.redhat.com/show_bug.cgi?id=2455329
- https://github.com/keycloak/keycloak
- https://github.com/keycloak/keycloak/releases/tag/26.6.2
