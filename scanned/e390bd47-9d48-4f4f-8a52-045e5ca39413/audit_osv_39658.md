# [H] Rocket.Chat: SAML signature validation skipped when IdP certificate field is empty

## Summary
Severity: High
Advisory: CVE-2026-46423
Aliases: GHSA-rgg7-qvp9-wvx7
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:L/SC:N/SI:N/SA:N)
Published: 2026-06-24
Source: https://osv.dev/vulnerability/CVE-2026-46423
Type: osv

## Details
Rocket.Chat is an open-source, secure, fully customizable communications platform. Prior to 8.5.0, 8.4.1, 8.3.3, 8.2.3, 8.1.4, 8.0.5, 7.13.7, and 7.10.11, Rocket.Chat's SAML service provider implementation silently skips both SAML Response and Assertion signature validation when the configured IdP certificate field is empty. The verifySignatures routine performs an early return when serviceProviderOptions.cert is falsy, which is the default state of the setting. Because provider registration only gates on the SAML "enabled" toggle and not on the presence of a certificate, an administrator who enables SAML without pasting an IdP certificate obtains a fully wired, publicly reachable SAML login endpoint that accepts unsigned or attacker-supplied assertions. This is a default-configuration authentication-bypass class: the fail-open branch is reached with no misconfiguration beyond leaving a field at its shipped default. This vulnerability is fixed in 8.5.0, 8.4.1, 8.3.3, 8.2.3, 8.1.4, 8.0.5, 7.13.7, and 7.10.11.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/46xxx/CVE-2026-46423.json
- https://github.com/RocketChat/Rocket.Chat/security/advisories/GHSA-rgg7-qvp9-wvx7
- https://nvd.nist.gov/vuln/detail/CVE-2026-46423
