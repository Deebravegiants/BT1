# Q1598: copy_attributes_from — copy preserves the key via caller-supplied id

## Question
Does `Auth::Session#copy_attributes_from` collapse two distinct identities into one when an unprivileged attacker submits the `id:` keyword, which lets a session be constructed under any storage key at `copy_attributes_from(other)`, which overwrites every attribute except `id`? Show that `copy_attributes_from` overwrites the shop and token while keeping the id, so a key silently starts pointing at a different tenant, that AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right is violated, and that the consequence is High - scope or expiry check bypass granting an operation the session was never authorized for.

## Target
- File/function: `lib/shopify_api/auth/session.rb` -> `Auth::Session#copy_attributes_from`
- Entrypoint: `copy_attributes_from(other)`, which overwrites every attribute except `id`
- Attacker controls: the `id:` keyword, which lets a session be constructed under any storage key
- Exploit idea: `copy_attributes_from` overwrites the shop and token while keeping the id, so a key silently starts pointing at a different tenant
- Invariant to test: AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right
- Expected Immunefi impact: High - scope or expiry check bypass granting an operation the session was never authorized for (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `copy_attributes_from` refuses to change `shop` on a session whose `id` encodes a different shop
