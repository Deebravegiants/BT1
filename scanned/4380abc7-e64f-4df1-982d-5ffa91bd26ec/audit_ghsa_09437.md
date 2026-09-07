# [H] Keycloak: Session fixation in OIDC login flow that can lead to account takeover

## Summary
Severity: High
Advisory: GHSA-hf67-5vvq-fm3r
CVE: CVE-2026-7507
CWE: CWE-290
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-05-19
Source: https://github.com/advisories/GHSA-hf67-5vvq-fm3r
Type: github-advisory

## Affected
- Maven: `org.keycloak:keycloak-services` — affected >=0 <26.6.2

## Details
A session fixation vulnerability was found in Keycloak's login-actions endpoints. An unauthenticated attacker could exploit this flaw by pre-creating an authentication session and tricking a victim into visiting a maliciously crafted link. By leveraging the /login-actions/restart endpoint—which processes session handles without adequate CSRF protection or cookie ownership validation—an attacker can reset the authentication flow state. This causes Single Sign-On (SSO) to authenticate the victim transparently upon clicking the link, allowing the attacker to hijack the required-action form without needing the victim's credentials. A successful exploit could lead to complete account takeover, including highly privileged administrative accounts.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-7507
- https://github.com/keycloak/keycloak/pull/49134
- https://github.com/keycloak/keycloak/commit/d791b270b9ea5203be40a9533c1c12c4d044fb52
- https://access.redhat.com/errata/RHSA-2026:19594
- https://access.redhat.com/errata/RHSA-2026:19595
- https://access.redhat.com/errata/RHSA-2026:19596
- https://access.redhat.com/errata/RHSA-2026:19597
- https://access.redhat.com/security/cve/CVE-2026-7507
- https://bugzilla.redhat.com/show_bug.cgi?id=2464145
- https://github.com/keycloak/keycloak
- https://github.com/keycloak/keycloak/releases/tag/26.6.2
