# [H] Dancer2::Plugin::Auth::OAuth::Provider versions before 0.23 for Perl do not support the OAuth 2.0 state parameter

## Summary
Severity: High
Advisory: CVE-2026-12746
CVSS: 8.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:N)
Published: 2026-07-04
Source: https://osv.dev/vulnerability/CVE-2026-12746
Type: osv

## Details
Dancer2::Plugin::Auth::OAuth::Provider versions before 0.23 for Perl do not support the OAuth 2.0 state parameter.

The authentication_url method builds the provider authorization redirect without issuing a state value, and the callback method exchanges the callback code and registers the resulting token into the session without verifying that the callback corresponds to an authorization request this session initiated.

Any application that uses this plugin for OAuth 2.0 login is exposed to login cross-site request forgery: because the callback is not bound to the session that began the flow, an attacker who starts an authorization with their own provider account can deliver the resulting callback to a victim, causing the victim's session to complete the attacker's authorization and associating the attacker's provider identity and access token with that session. Where the application persists this as an account link, the attacker may retain access to the victim's account through their own provider credentials.

## References
- http://www.openwall.com/lists/oss-security/2026/07/04/9
- https://cpan.org/modules
- https://metacpan.org/release/BIAFRA/Dancer2-Plugin-Auth-OAuth-0.23/diff/BIAFRA/Dancer2-Plugin-Auth-OAuth-0.22
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/12xxx/CVE-2026-12746.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-12746
- https://github.com/biafra/perl-Dancer2-Plugin-Auth-OAuth/commit/806420fc2abbe13bede4461475f2f3dcd7daf5f2.patch
- https://github.com/biafra/perl-Dancer2-Plugin-Auth-OAuth
- https://datatracker.ietf.org/doc/html/rfc6749#section-10.12
