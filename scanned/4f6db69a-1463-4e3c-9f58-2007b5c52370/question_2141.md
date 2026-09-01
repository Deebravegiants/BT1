# Q2141: refresh_token_expired? — id and shop can disagree via shop with separator

## Question
Is there a reachable state in which an unprivileged attacker, controlling a `shop` containing `_` so `"#{shop}_#{user_id}"` collides with another shop/user pair at `refresh_token_expired?`, which returns false whenever `@refresh_token_expires` is nil, makes `Auth::Session#refresh_token_expired?` return a result the caller treats as authenticated, given that `id` is caller-controlled and never re-derived from `shop`, so the storage key and the shop it holds a token for can differ? Test SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host and quantify Critical - cross-user access inside one shop: one staff user's online session is served to another.

## Target
- File/function: `lib/shopify_api/auth/session.rb` -> `Auth::Session#refresh_token_expired?`
- Entrypoint: `refresh_token_expired?`, which returns false whenever `@refresh_token_expires` is nil
- Attacker controls: a `shop` containing `_` so `"#{shop}_#{user_id}"` collides with another shop/user pair
- Exploit idea: `id` is caller-controlled and never re-derived from `shop`, so the storage key and the shop it holds a token for can differ
- Invariant to test: SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host
- Expected Immunefi impact: Critical - cross-user access inside one shop: one staff user's online session is served to another (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `copy_attributes_from` refuses to change `shop` on a session whose `id` encodes a different shop
