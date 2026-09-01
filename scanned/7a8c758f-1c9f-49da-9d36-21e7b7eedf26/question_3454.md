# Q3454: offline_session_id — interpolation collision via non-embedded config

## Question
If an unprivileged attacker submits an app configured `is_embedded: false`, where the cookie is the only accepted credential to `offline_session_id(shop)`, a bare `"offline_#{shop}"` interpolation, does `SessionUtils.offline_session_id` end up acting on a value that was never authenticated, because string concatenation with `_` makes distinct identities collide? Close the question on SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source and on Critical - theft of a merchant's refresh token, granting durable access after rotation.

## Target
- File/function: `lib/shopify_api/utils/session_utils.rb` -> `SessionUtils.offline_session_id`
- Entrypoint: `offline_session_id(shop)`, a bare `"offline_#{shop}"` interpolation
- Attacker controls: an app configured `is_embedded: false`, where the cookie is the only accepted credential
- Exploit idea: string concatenation with `_` makes distinct identities collide
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: Critical - theft of a merchant's refresh token, granting durable access after rotation (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert an embedded app rejects a request with no `Authorization` header rather than falling back to the cookie
