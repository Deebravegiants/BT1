# Q2351: == — no vocabulary validation via scope string from a token response

## Question
Is there a reachable state in which an unprivileged attacker, controlling the `scope` / `associated_user_scope` strings returned with an access token and stored on the session at `AuthScopes#==` and `hash`, which compare only `compressed_scopes`, makes `Auth::AuthScopes#==` return a result the caller treats as authenticated, given that any string is accepted as a scope, so a scope check can be satisfied by a name Shopify never issued? Test SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source and quantify Critical - cross-user access inside one shop: one staff user's online session is served to another.

## Target
- File/function: `lib/shopify_api/auth/auth_scopes.rb` -> `Auth::AuthScopes#==`
- Entrypoint: `AuthScopes#==` and `hash`, which compare only `compressed_scopes`
- Attacker controls: the `scope` / `associated_user_scope` strings returned with an access token and stored on the session
- Exploit idea: any string is accepted as a scope, so a scope check can be satisfied by a name Shopify never issued
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: Critical - cross-user access inside one shop: one staff user's online session is served to another (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `==` distinguishes two scope sets whose expanded permissions differ
