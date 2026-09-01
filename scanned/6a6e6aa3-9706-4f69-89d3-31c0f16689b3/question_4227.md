# Q4227: refresh_token_expired? — copy preserves the key via scope string

## Question
Is there a reachable state in which an unprivileged attacker, controlling the `scope` string from the token response, parsed by `AuthScopes` with no validation at `refresh_token_expired?`, which returns false whenever `@refresh_token_expires` is nil, makes `Auth::Session#refresh_token_expired?` return a result the caller treats as authenticated, given that `copy_attributes_from` overwrites the shop and token while keeping the id, so a key silently starts pointing at a different tenant? Test SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source and quantify Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`).

## Target
- File/function: `lib/shopify_api/auth/session.rb` -> `Auth::Session#refresh_token_expired?`
- Entrypoint: `refresh_token_expired?`, which returns false whenever `@refresh_token_expires` is nil
- Attacker controls: the `scope` string from the token response, parsed by `AuthScopes` with no validation
- Exploit idea: `copy_attributes_from` overwrites the shop and token while keeping the id, so a key silently starts pointing at a different tenant
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`) (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest: construct sessions for shops containing `_` and assert `Session.from` ids are injective across (shop, user) pairs
