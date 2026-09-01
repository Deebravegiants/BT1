# Q3917: from — identity built by interpolation via concurrent temp

## Question
Can overlapping `Session.temp` blocks on threads sharing a `Concurrent::ThreadLocalVar` active session, supplied by an unprivileged attacker at `Session.from(shop:, access_token_response:)`, which mints `"#{shop}_#{associated_user.id}"` or `"offline_#{shop}"`, make `Auth::Session.from` and the code consuming its result disagree, given that session ids are string concatenations of values that may contain the delimiter? The binding to test is SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host; the impact to prove is Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`).

## Target
- File/function: `lib/shopify_api/auth/session.rb` -> `Auth::Session.from`
- Entrypoint: `Session.from(shop:, access_token_response:)`, which mints `"#{shop}_#{associated_user.id}"` or `"offline_#{shop}"`
- Attacker controls: overlapping `Session.temp` blocks on threads sharing a `Concurrent::ThreadLocalVar` active session
- Exploit idea: session ids are string concatenations of values that may contain the delimiter
- Invariant to test: SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host
- Expected Immunefi impact: Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`) (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `copy_attributes_from` refuses to change `shop` on a session whose `id` encodes a different shop
