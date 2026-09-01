# Q2298: from — copy preserves the key via online/offline flip

## Question
Does `Auth::Session.from` collapse two distinct identities into one when an unprivileged attacker submits an `is_online` value inconsistent with `associated_user`, since `@is_online` defaults to `!associated_user.nil?` at `Session.from(shop:, access_token_response:)`, which mints `"#{shop}_#{associated_user.id}"` or `"offline_#{shop}"`? Show that `copy_attributes_from` overwrites the shop and token while keeping the id, so a key silently starts pointing at a different tenant, that AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right is violated, and that the consequence is High - scope or expiry check bypass granting an operation the session was never authorized for.

## Target
- File/function: `lib/shopify_api/auth/session.rb` -> `Auth::Session.from`
- Entrypoint: `Session.from(shop:, access_token_response:)`, which mints `"#{shop}_#{associated_user.id}"` or `"offline_#{shop}"`
- Attacker controls: an `is_online` value inconsistent with `associated_user`, since `@is_online` defaults to `!associated_user.nil?`
- Exploit idea: `copy_attributes_from` overwrites the shop and token while keeping the id, so a key silently starts pointing at a different tenant
- Invariant to test: AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right
- Expected Immunefi impact: High - scope or expiry check bypass granting an operation the session was never authorized for (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest: construct sessions for shops containing `_` and assert `Session.from` ids are injective across (shop, user) pairs
