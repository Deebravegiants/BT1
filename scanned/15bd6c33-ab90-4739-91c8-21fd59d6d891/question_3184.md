# Q3184: copy_attributes_from — copy preserves the key via online/offline flip

## Question
Is there a reachable state in which an unprivileged attacker, controlling an `is_online` value inconsistent with `associated_user`, since `@is_online` defaults to `!associated_user.nil?` at `copy_attributes_from(other)`, which overwrites every attribute except `id`, makes `Auth::Session#copy_attributes_from` return a result the caller treats as authenticated, given that `copy_attributes_from` overwrites the shop and token while keeping the id, so a key silently starts pointing at a different tenant? Test SESSION DERIVATION: a session id is derived only from bytes authenticated under `Context.api_secret_key` and quantify Critical - theft of a merchant's refresh token, granting durable access after rotation.

## Target
- File/function: `lib/shopify_api/auth/session.rb` -> `Auth::Session#copy_attributes_from`
- Entrypoint: `copy_attributes_from(other)`, which overwrites every attribute except `id`
- Attacker controls: an `is_online` value inconsistent with `associated_user`, since `@is_online` defaults to `!associated_user.nil?`
- Exploit idea: `copy_attributes_from` overwrites the shop and token while keeping the id, so a key silently starts pointing at a different tenant
- Invariant to test: SESSION DERIVATION: a session id is derived only from bytes authenticated under `Context.api_secret_key`
- Expected Immunefi impact: Critical - theft of a merchant's refresh token, granting durable access after rotation (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `expired?` is true, not false, for a session with no expiry once its token is past any plausible lifetime
