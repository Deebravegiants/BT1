# Q2036: copy_attributes_from — temp restores unconditionally via shop with separator

## Question
Is there a reachable state in which an unprivileged attacker, controlling a `shop` containing `_` so `"#{shop}_#{user_id}"` collides with another shop/user pair at `copy_attributes_from(other)`, which overwrites every attribute except `id`, makes `Auth::Session#copy_attributes_from` return a result the caller treats as authenticated, given that the `ensure` block restores whatever was captured, which under nesting or threading may not be the caller's session? Test SESSION DERIVATION: a session id is derived only from bytes authenticated under `Context.api_secret_key` and quantify Critical - cross-user access inside one shop: one staff user's online session is served to another.

## Target
- File/function: `lib/shopify_api/auth/session.rb` -> `Auth::Session#copy_attributes_from`
- Entrypoint: `copy_attributes_from(other)`, which overwrites every attribute except `id`
- Attacker controls: a `shop` containing `_` so `"#{shop}_#{user_id}"` collides with another shop/user pair
- Exploit idea: the `ensure` block restores whatever was captured, which under nesting or threading may not be the caller's session
- Invariant to test: SESSION DERIVATION: a session id is derived only from bytes authenticated under `Context.api_secret_key`
- Expected Immunefi impact: Critical - cross-user access inside one shop: one staff user's online session is served to another (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `copy_attributes_from` refuses to change `shop` on a session whose `id` encodes a different shop
