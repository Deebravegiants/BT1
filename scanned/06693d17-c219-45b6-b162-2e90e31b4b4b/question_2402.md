# Q2402: copy_attributes_from — equality omits the token via scope string

## Question
Starting from `copy_attributes_from(other)`, which overwrites every attribute except `id`, can an unprivileged attacker supply the `scope` string from the token response, parsed by `AuthScopes` with no validation so that `Session#==` compares many fields; a caller using it to decide sameness may treat two sessions with different credentials as equal? Determine whether AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right still holds through `Auth::Session#copy_attributes_from`, and whether the result reaches Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`).

## Target
- File/function: `lib/shopify_api/auth/session.rb` -> `Auth::Session#copy_attributes_from`
- Entrypoint: `copy_attributes_from(other)`, which overwrites every attribute except `id`
- Attacker controls: the `scope` string from the token response, parsed by `AuthScopes` with no validation
- Exploit idea: `Session#==` compares many fields; a caller using it to decide sameness may treat two sessions with different credentials as equal
- Invariant to test: AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right
- Expected Immunefi impact: Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`) (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `copy_attributes_from` refuses to change `shop` on a session whose `id` encodes a different shop
