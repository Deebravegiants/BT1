# [H] Auth Proxy IPv6 whitelist bypass

## Summary
Severity: High
Advisory: BIT-grafana-2026-33376
Aliases: CVE-2026-33376
Ecosystem: Bitnami
Published: 2026-05-15
Source: https://osv.dev/vulnerability/BIT-grafana-2026-33376
Type: osv

## Affected
- Bitnami: `grafana` — affected >=13.0.0 <13.0.1

## Details
When using an IPv6 allow-list for the Auth Proxy feature, it defaults to /32 addresses. Addresses specifying a mask explicitly are not affected; to mitigate easily, add the desired mask (usually /128) to the addresses. Only auth proxy is affected; Okta, SAML, LDAP, etc are unaffected here.

## References
- https://grafana.com/security/security-advisories/cve-2026-33376
- https://nvd.nist.gov/vuln/detail/CVE-2026-33376
