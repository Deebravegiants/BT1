# Q2454: temp — copy preserves the key via concurrent temp

## Question
Can overlapping `Session.temp` blocks on threads sharing a `Concurrent::ThreadLocalVar` active session, supplied by an unprivileged attacker at `Session.temp(shop:, access_token:)`, which swaps `Context.active_session` around a block, make `Auth::Session.temp` and the code consuming its result disagree, given that `copy_attributes_from` overwrites the shop and token while keeping the id, so a key silently starts pointing at a different tenant? The binding to test is AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right; the impact to prove is Critical - theft of a merchant's refresh token, granting durable access after rotation.

## Target
- File/function: `lib/shopify_api/auth/session.rb` -> `Auth::Session.temp`
- Entrypoint: `Session.temp(shop:, access_token:)`, which swaps `Context.active_session` around a block
- Attacker controls: overlapping `Session.temp` blocks on threads sharing a `Concurrent::ThreadLocalVar` active session
- Exploit idea: `copy_attributes_from` overwrites the shop and token while keeping the id, so a key silently starts pointing at a different tenant
- Invariant to test: AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right
- Expected Immunefi impact: Critical - theft of a merchant's refresh token, granting durable access after rotation (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest: construct sessions for shops containing `_` and assert `Session.from` ids are injective across (shop, user) pairs
