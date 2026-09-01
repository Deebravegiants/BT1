# Q3977: == — copy preserves the key via concurrent temp

## Question
Starting from `Session#==`, used by callers to decide whether a stored session matches, can an unprivileged attacker supply overlapping `Session.temp` blocks on threads sharing a `Concurrent::ThreadLocalVar` active session so that `copy_attributes_from` overwrites the shop and token while keeping the id, so a key silently starts pointing at a different tenant? Determine whether SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host still holds through `Auth::Session#==`, and whether the result reaches Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`).

## Target
- File/function: `lib/shopify_api/auth/session.rb` -> `Auth::Session#==`
- Entrypoint: `Session#==`, used by callers to decide whether a stored session matches
- Attacker controls: overlapping `Session.temp` blocks on threads sharing a `Concurrent::ThreadLocalVar` active session
- Exploit idea: `copy_attributes_from` overwrites the shop and token while keeping the id, so a key silently starts pointing at a different tenant
- Invariant to test: SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host
- Expected Immunefi impact: Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`) (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `copy_attributes_from` refuses to change `shop` on a session whose `id` encodes a different shop
