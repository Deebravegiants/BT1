# [M] Rocket.Chat: Lack of SAML Signature Check During Logout Could Lead To DoS

## Summary
Severity: Medium
Advisory: CVE-2026-45677
Aliases: GHSA-pw6f-q8ww-vqfq
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-06-24
Source: https://osv.dev/vulnerability/CVE-2026-45677
Type: osv

## Details
Rocket.Chat is an open-source, secure, fully customizable communications platform. Prior to 8.5.0, 8.4.1, 8.3.3, 8.2.3, 8.1.4, 8.0.5, 7.13.7, and 7.10.11, Rocket.Chat's SAML integration does not verify the signature on inbound LogoutRequest messages. An unauthenticated remote attacker who knows a target user's SAML NameID - which major identity providers (Okta, Google Workspace, Microsoft Entra ID, JumpCloud) expose as the user's email address - can craft a valid-looking unsigned LogoutRequest and submit it to the SP logout endpoint. The server processes it as legitimate, immediately destroying the victim's session. Because the attack requires no authentication and no interaction from the victim, it can be repeated in a loop against individual users or scripted across many accounts, effectively rendering the Rocket.Chat instance unusable for SAML-authenticated users. This vulnerability is fixed in 8.5.0, 8.4.1, 8.3.3, 8.2.3, 8.1.4, 8.0.5, 7.13.7, and 7.10.11.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/45xxx/CVE-2026-45677.json
- https://github.com/RocketChat/Rocket.Chat/security/advisories/GHSA-pw6f-q8ww-vqfq
- https://nvd.nist.gov/vuln/detail/CVE-2026-45677
