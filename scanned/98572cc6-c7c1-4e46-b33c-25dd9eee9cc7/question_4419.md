# Q4419: copy_attributes_from — id and shop can disagree via nil expires

## Question
Does `Auth::Session#copy_attributes_from` collapse two distinct identities into one when an unprivileged attacker submits an access-token response with no `expires_in`, leaving `@expires` nil and `expired?` permanently false at `copy_attributes_from(other)`, which overwrites every attribute except `id`? Show that `id` is caller-controlled and never re-derived from `shop`, so the storage key and the shop it holds a token for can differ, that SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source is violated, and that the consequence is Critical - theft of a merchant's refresh token, granting durable access after rotation.

## Target
- File/function: `lib/shopify_api/auth/session.rb` -> `Auth::Session#copy_attributes_from`
- Entrypoint: `copy_attributes_from(other)`, which overwrites every attribute except `id`
- Attacker controls: an access-token response with no `expires_in`, leaving `@expires` nil and `expired?` permanently false
- Exploit idea: `id` is caller-controlled and never re-derived from `shop`, so the storage key and the shop it holds a token for can differ
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: Critical - theft of a merchant's refresh token, granting durable access after rotation (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest: construct sessions for shops containing `_` and assert `Session.from` ids are injective across (shop, user) pairs
