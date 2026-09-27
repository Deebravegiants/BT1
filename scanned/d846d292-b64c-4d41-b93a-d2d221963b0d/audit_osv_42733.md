# [M] Doorkeeper OpenID Connect: DCR endpoint persists unvalidated client-supplied scopes

## Summary
Severity: Medium
Advisory: CVE-2026-70665
Aliases: GHSA-8r7r-wh7x-27ff
CVSS: 4.2 (CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:L/I:L/A:N)
Published: 2026-08-25
Source: https://osv.dev/vulnerability/CVE-2026-70665
Type: osv

## Details
Doorkeeper OpenID Connect implements an OpenID Connect authentication provider for Rails applications on top of Doorkeeper. Prior to 1.10.4, the Dynamic Client Registration (DCR) endpoint persists client-supplied scopes without validating them against the server's configured scope set. Under certain conditions, this allows a self-registered client to obtain scopes beyond what the server intended to grant. In DynamicClientRegistrationController#application_params, the scopes attribute is assigned directly from params[:scope] with no validation against Doorkeeper.configuration.scopes or optional_scopes. Combined with enforce_configured_scopes being off by default and Doorkeeper's ScopeChecker prioritizing application-level scopes over server-level scopes, this creates a privilege escalation path. This issue is fixed in version 1.10.4.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/70xxx/CVE-2026-70665.json
- https://github.com/doorkeeper-gem/doorkeeper-openid_connect/security/advisories/GHSA-8r7r-wh7x-27ff
- https://nvd.nist.gov/vuln/detail/CVE-2026-70665
- https://github.com/doorkeeper-gem/doorkeeper-openid_connect/commit/24c3cb1729b69f48649a6f4491dcae69f805000d
