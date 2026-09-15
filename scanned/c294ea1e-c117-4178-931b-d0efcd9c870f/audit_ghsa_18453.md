# [M] Keycloak phishing attack via email verification step in first login flow

## Summary
Severity: Medium
Advisory: GHSA-xhpr-465j-7p9q
CVE: CVE-2025-7365
CWE: CWE-346
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:R/S:U/C:H/I:L/A:N (CVSS_V3)
Published: 2025-07-30
Source: https://github.com/advisories/GHSA-xhpr-465j-7p9q
Type: github-advisory

## Affected
- Maven: `org.keycloak:keycloak-services` — affected >=0 <26.0.13
- Maven: `org.keycloak:keycloak-services` — affected >=26.2.0 <26.2.6

## Details
There is a flaw with the first login flow where, during a IdP login, an attacker with a registered account can initiate the process to merge accounts with an existing victim's account. The attacker will subsequently be prompted to "review profile" information, which allows the the attacker to modify their email address to that of a victim's account. This triggers a verification email sent to the victim's email address. If the victim clicks the verification link, the attacker can gain access to the victim's account. While not a zero-interaction attack, the attacker's email address is not directly present in the verification email content, making it a potential phishing opportunity. 

This issue has been fixed in versions 26.0.13, 26.2.6, and 26.3.0.

## References
- https://github.com/keycloak/keycloak/security/advisories/GHSA-xhpr-465j-7p9q
- https://nvd.nist.gov/vuln/detail/CVE-2025-7365
- https://github.com/keycloak/keycloak/issues/40446
- https://github.com/keycloak/keycloak/pull/40520
- https://access.redhat.com/errata/RHSA-2025:11986
- https://access.redhat.com/errata/RHSA-2025:11987
- https://access.redhat.com/errata/RHSA-2025:12015
- https://access.redhat.com/errata/RHSA-2025:12016
- https://access.redhat.com/security/cve/CVE-2025-7365
- https://bugzilla.redhat.com/show_bug.cgi?id=2378852
- https://github.com/keycloak/keycloak
- https://github.com/keycloak/keycloak/releases/tag/26.0.13
- https://github.com/keycloak/keycloak/releases/tag/26.2.6
- https://github.com/keycloak/keycloak/releases/tag/26.3.0
