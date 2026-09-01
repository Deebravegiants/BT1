# Q3797: refresh_token_expired? — id and shop can disagree via nil expires

## Question
If an unprivileged attacker submits an access-token response with no `expires_in`, leaving `@expires` nil and `expired?` permanently false to `refresh_token_expired?`, which returns false whenever `@refresh_token_expires` is nil, does `Auth::Session#refresh_token_expired?` end up acting on a value that was never authenticated, because `id` is caller-controlled and never re-derived from `shop`, so the storage key and the shop it holds a token for can differ? Close the question on SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host and on Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`).

## Target
- File/function: `lib/shopify_api/auth/session.rb` -> `Auth::Session#refresh_token_expired?`
- Entrypoint: `refresh_token_expired?`, which returns false whenever `@refresh_token_expires` is nil
- Attacker controls: an access-token response with no `expires_in`, leaving `@expires` nil and `expired?` permanently false
- Exploit idea: `id` is caller-controlled and never re-derived from `shop`, so the storage key and the shop it holds a token for can differ
- Invariant to test: SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host
- Expected Immunefi impact: Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`) (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `copy_attributes_from` refuses to change `shop` on a session whose `id` encodes a different shop
