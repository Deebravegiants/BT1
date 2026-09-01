# Q876: initialize — ambiguous concatenation via key-order dependence

## Question
Starting from `AuthQuery.new(code:, shop:, timestamp:, state:, host:, hmac:)`, built by the host app directly from the callback query string, can an unprivileged attacker supply a query string whose parameter order differs from the fixed hash order used in `to_signable_string` so that two different parameter sets serialise to the same signable string? Determine whether SIGNATURE COVERAGE: every value acted on downstream is inside the string handed to `HmacValidator` via `to_signable_string` still holds through `AuthQuery#initialize`, and whether the result reaches Critical - authentication bypass: a forged or unsigned request is accepted as authentic by the app.

## Target
- File/function: `lib/shopify_api/auth/oauth/auth_query.rb` -> `AuthQuery#initialize`
- Entrypoint: `AuthQuery.new(code:, shop:, timestamp:, state:, host:, hmac:)`, built by the host app directly from the callback query string
- Attacker controls: a query string whose parameter order differs from the fixed hash order used in `to_signable_string`
- Exploit idea: two different parameter sets serialise to the same signable string
- Invariant to test: SIGNATURE COVERAGE: every value acted on downstream is inside the string handed to `HmacValidator` via `to_signable_string`
- Expected Immunefi impact: Critical - authentication bypass: a forged or unsigned request is accepted as authentic by the app (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest: build the query two ways, assert `HmacValidator.validate` accepts both, and diff the two `to_signable_string` outputs
