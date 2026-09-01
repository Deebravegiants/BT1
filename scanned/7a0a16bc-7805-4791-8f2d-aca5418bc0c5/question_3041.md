# Q3041: refresh_token_expired? — copy preserves the key via nil expires

## Question
If an unprivileged attacker submits an access-token response with no `expires_in`, leaving `@expires` nil and `expired?` permanently false to `refresh_token_expired?`, which returns false whenever `@refresh_token_expires` is nil, does `Auth::Session#refresh_token_expired?` end up acting on a value that was never authenticated, because `copy_attributes_from` overwrites the shop and token while keeping the id, so a key silently starts pointing at a different tenant? Close the question on SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host and on Critical - cross-user access inside one shop: one staff user's online session is served to another.

## Target
- File/function: `lib/shopify_api/auth/session.rb` -> `Auth::Session#refresh_token_expired?`
- Entrypoint: `refresh_token_expired?`, which returns false whenever `@refresh_token_expires` is nil
- Attacker controls: an access-token response with no `expires_in`, leaving `@expires` nil and `expired?` permanently false
- Exploit idea: `copy_attributes_from` overwrites the shop and token while keeping the id, so a key silently starts pointing at a different tenant
- Invariant to test: SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host
- Expected Immunefi impact: Critical - cross-user access inside one shop: one staff user's online session is served to another (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `copy_attributes_from` refuses to change `shop` on a session whose `id` encodes a different shop
