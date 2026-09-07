# [M] Keycloak Open Redirect vulnerability

## Summary
Severity: Medium
Advisory: GHSA-g4gc-rh26-m3p5
CVE: CVE-2024-7260
CWE: CWE-601
Ecosystem: Maven
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2024-09-09
Source: https://github.com/advisories/GHSA-g4gc-rh26-m3p5
Type: github-advisory

## Affected
- Maven: `org.keycloak:keycloak-core` — affected >=0 <24.0.7

## Details
An open redirect vulnerability was found in Keycloak. A specially crafted URL can be constructed where the `referrer` and `referrer_uri` parameters are made to trick a user to visit a malicious webpage. A trusted URL can trick users and automation into believing that the URL is safe, when, in fact, it redirects to a malicious server. This issue can result in a victim inadvertently trusting the destination of the redirect, potentially leading to a successful phishing attack or other types of attacks.

Once a crafted URL is made, it can be sent to a Keycloak admin via email for example. This will trigger this vulnerability when the user visits the page and clicks the link. A malicious actor can use this to target users they know are Keycloak admins for further attacks. It may also be possible to bypass other domain-related security checks, such as supplying this as a OAuth redirect uri. The malicious actor can further obfuscate the `redirect_uri` using URL encoding, to hide the text of the actual malicious website domain.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-7260
- https://access.redhat.com/errata/RHSA-2024:6502
- https://access.redhat.com/errata/RHSA-2024:6503
- https://access.redhat.com/security/cve/CVE-2024-7260
- https://bugzilla.redhat.com/show_bug.cgi?id=2301875
- https://github.com/keycloak/keycloak
