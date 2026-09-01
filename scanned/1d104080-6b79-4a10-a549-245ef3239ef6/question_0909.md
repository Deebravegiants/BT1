# Q909: copy_attributes_from — id and shop can disagree via concurrent temp

## Question
Is there a reachable state in which an unprivileged attacker, controlling overlapping `Session.temp` blocks on threads sharing a `Concurrent::ThreadLocalVar` active session at `copy_attributes_from(other)`, which overwrites every attribute except `id`, makes `Auth::Session#copy_attributes_from` return a result the caller treats as authenticated, given that `id` is caller-controlled and never re-derived from `shop`, so the storage key and the shop it holds a token for can differ? Test SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host and quantify Critical - theft of a merchant's refresh token, granting durable access after rotation.

## Target
- File/function: `lib/shopify_api/auth/session.rb` -> `Auth::Session#copy_attributes_from`
- Entrypoint: `copy_attributes_from(other)`, which overwrites every attribute except `id`
- Attacker controls: overlapping `Session.temp` blocks on threads sharing a `Concurrent::ThreadLocalVar` active session
- Exploit idea: `id` is caller-controlled and never re-derived from `shop`, so the storage key and the shop it holds a token for can differ
- Invariant to test: SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host
- Expected Immunefi impact: Critical - theft of a merchant's refresh token, granting durable access after rotation (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest: construct sessions for shops containing `_` and assert `Session.from` ids are injective across (shop, user) pairs
