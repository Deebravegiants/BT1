# Q3525: == — id and shop can disagree via associated_user id

## Question
Can the `associated_user.id` from the token response, interpolated into the session id, supplied by an unprivileged attacker at `Session#==`, used by callers to decide whether a stored session matches, make `Auth::Session#==` and the code consuming its result disagree, given that `id` is caller-controlled and never re-derived from `shop`, so the storage key and the shop it holds a token for can differ? The binding to test is SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host; the impact to prove is Critical - cross-tenant access: one shop's request reads or mutates another merchant's data.

## Target
- File/function: `lib/shopify_api/auth/session.rb` -> `Auth::Session#==`
- Entrypoint: `Session#==`, used by callers to decide whether a stored session matches
- Attacker controls: the `associated_user.id` from the token response, interpolated into the session id
- Exploit idea: `id` is caller-controlled and never re-derived from `shop`, so the storage key and the shop it holds a token for can differ
- Invariant to test: SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host
- Expected Immunefi impact: Critical - cross-tenant access: one shop's request reads or mutates another merchant's data (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest: construct sessions for shops containing `_` and assert `Session.from` ids are injective across (shop, user) pairs
