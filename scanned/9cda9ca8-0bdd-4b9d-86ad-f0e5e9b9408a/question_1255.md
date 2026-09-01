# Q1255: covers? — implication is textual via delimiter in a scope name

## Question
Does `Auth::AuthScopes#covers?` collapse two distinct identities into one when an unprivileged attacker submits a scope name containing `,` so one entry becomes two at `AuthScopes#covers?(auth_scopes)`, which apps call to decide whether a session may perform an operation? Show that `implied_scope` derives an implication from string shape alone, with no allow-list of real Shopify scopes, that SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source is violated, and that the consequence is Critical - cross-tenant access: one shop's request reads or mutates another merchant's data.

## Target
- File/function: `lib/shopify_api/auth/auth_scopes.rb` -> `Auth::AuthScopes#covers?`
- Entrypoint: `AuthScopes#covers?(auth_scopes)`, which apps call to decide whether a session may perform an operation
- Attacker controls: a scope name containing `,` so one entry becomes two
- Exploit idea: `implied_scope` derives an implication from string shape alone, with no allow-list of real Shopify scopes
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: Critical - cross-tenant access: one shop's request reads or mutates another merchant's data (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `AuthScopes.new('write_x').covers?(AuthScopes.new('read_x'))` cannot be reached with a fabricated `x`
