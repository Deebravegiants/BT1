# [M] Doorkeeper Openid Connect: Dynamic Client Registration feature creates public clients with client_secret

## Summary
Severity: Medium
Advisory: GHSA-m6vc-f87m-cc2h
CVE: CVE-2026-44476
CWE: CWE-290
Ecosystem: RubyGems
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:L/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-06-04
Source: https://github.com/advisories/GHSA-m6vc-f87m-cc2h
Type: github-advisory

## Affected
- RubyGems: `doorkeeper-openid_connect` — affected >=1.9.0 <1.10.0

## Details
### Impact

The `DynamicClientRegistrationController#register` action hard-codes `confidential: false` when creating applications (dynamic_client_registration_controller.rb:18-25), yet the response includes a client_secret and advertises `token_endpoint_auth_methods_supported: ["client_secret_basic", "client_secret_post"]`.

Because Doorkeeper's `Application.by_uid_and_secret` treats a blank/missing secret as valid for non-confidential (public) clients, an
attacker who knows only the client_id (which is public information) can authenticate as the dynamically-registered client at the token endpoint.

**Note** that Dynamic Client Registration is opt-in feature which is disabled by default so only projects that explicitly enabled it are affected.

**Steps to Reproduce**

1. Enable dynamic client registration in the initializer
2. POST /oauth/registration with client_name, redirect_uris, and scope
3. Observe: response returns client_secret, but the created
Doorkeeper::Application has confidential: false
4. Call `Doorkeeper::Application.by_uid_and_secret(client_id, nil)` — it
returns the application (credentials bypass)
5. POST /oauth/token with grant_type=client_credentials and only
client_id (no client_secret) — the token endpoint issues an access token
without any secret verification


### Patches
Patched in 1.10.0

### Workarounds
Upgrade existing applications created with a Dynamic Client registration to have `confidential: true`

## References
- https://github.com/doorkeeper-gem/doorkeeper-openid_connect/security/advisories/GHSA-m6vc-f87m-cc2h
- https://github.com/doorkeeper-gem/doorkeeper-openid_connect
- https://github.com/doorkeeper-gem/doorkeeper-openid_connect/releases/tag/v1.10.0
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/doorkeeper-openid_connect/CVE-2026-44476.yml
- https://www.cve.org/CVERecord?id=CVE-2026-44476
