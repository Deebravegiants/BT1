# Q931: store_scopes — no vocabulary validation via compressed vs expanded asymmetry

## Question
Can an unprivileged attacker reach `Auth::AuthScopes#store_scopes` through the private `store_scopes`, which builds `compressed_scopes` and `expanded_scopes` while supplying a comparison where the caller's required scopes are compressed and the session's are expanded, so that any string is accepted as a scope, so a scope check can be satisfied by a name Shopify never issued, breaking the requirement that SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source, and ending in Critical - cross-tenant access: one shop's request reads or mutates another merchant's data?

## Target
- File/function: `lib/shopify_api/auth/auth_scopes.rb` -> `Auth::AuthScopes#store_scopes`
- Entrypoint: the private `store_scopes`, which builds `compressed_scopes` and `expanded_scopes`
- Attacker controls: a comparison where the caller's required scopes are compressed and the session's are expanded
- Exploit idea: any string is accepted as a scope, so a scope check can be satisfied by a name Shopify never issued
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: Critical - cross-tenant access: one shop's request reads or mutates another merchant's data (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `AuthScopes.new('write_x').covers?(AuthScopes.new('read_x'))` cannot be reached with a fabricated `x`
