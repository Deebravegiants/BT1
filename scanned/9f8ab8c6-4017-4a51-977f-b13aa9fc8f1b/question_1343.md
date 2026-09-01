# Q1343: store_scopes — implication is textual via scope string from a token response

## Question
Is there a reachable state in which an unprivileged attacker, controlling the `scope` / `associated_user_scope` strings returned with an access token and stored on the session at the private `store_scopes`, which builds `compressed_scopes` and `expanded_scopes`, makes `Auth::AuthScopes#store_scopes` return a result the caller treats as authenticated, given that `implied_scope` derives an implication from string shape alone, with no allow-list of real Shopify scopes? Test SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source and quantify Critical - cross-user access inside one shop: one staff user's online session is served to another.

## Target
- File/function: `lib/shopify_api/auth/auth_scopes.rb` -> `Auth::AuthScopes#store_scopes`
- Entrypoint: the private `store_scopes`, which builds `compressed_scopes` and `expanded_scopes`
- Attacker controls: the `scope` / `associated_user_scope` strings returned with an access token and stored on the session
- Exploit idea: `implied_scope` derives an implication from string shape alone, with no allow-list of real Shopify scopes
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: Critical - cross-user access inside one shop: one staff user's online session is served to another (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `==` distinguishes two scope sets whose expanded permissions differ
