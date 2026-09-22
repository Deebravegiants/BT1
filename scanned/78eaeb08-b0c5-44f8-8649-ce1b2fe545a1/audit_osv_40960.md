# [H] Capgo - Cross-Organization Account Disruption via SSO Prelink Endpoint

## Summary
Severity: High
Advisory: CVE-2026-56313
Aliases: GHSA-x3vq-34gg-cwq7
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-07-12
Source: https://osv.dev/vulnerability/CVE-2026-56313
Type: osv

## Details
Capgo before 12.128.2 contains a cross-organization account disruption vulnerability in the SSO prelink endpoint that allows enterprise administrators to delete password identities of users in foreign organizations. Attackers with org.update_settings permission and an active SSO provider can call the prelink-users endpoint to permanently remove email-based authentication for any user matching the provider's email domain, forcing victims to use the attacker's SSO provider or complete password reset recovery.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/56xxx/CVE-2026-56313.json
- https://github.com/Cap-go/capgo/security/advisories/GHSA-x3vq-34gg-cwq7
- https://nvd.nist.gov/vuln/detail/CVE-2026-56313
- https://www.vulncheck.com/advisories/capgo-cross-organization-account-disruption-via-sso-prelink-endpoint
