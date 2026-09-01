# Q2201: refresh_token_expired? — temp restores unconditionally via caller-supplied id

## Question
If an unprivileged attacker submits the `id:` keyword, which lets a session be constructed under any storage key to `refresh_token_expired?`, which returns false whenever `@refresh_token_expires` is nil, does `Auth::Session#refresh_token_expired?` end up acting on a value that was never authenticated, because the `ensure` block restores whatever was captured, which under nesting or threading may not be the caller's session? Close the question on SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host and on Critical - cross-user access inside one shop: one staff user's online session is served to another.

## Target
- File/function: `lib/shopify_api/auth/session.rb` -> `Auth::Session#refresh_token_expired?`
- Entrypoint: `refresh_token_expired?`, which returns false whenever `@refresh_token_expires` is nil
- Attacker controls: the `id:` keyword, which lets a session be constructed under any storage key
- Exploit idea: the `ensure` block restores whatever was captured, which under nesting or threading may not be the caller's session
- Invariant to test: SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host
- Expected Immunefi impact: Critical - cross-user access inside one shop: one staff user's online session is served to another (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `copy_attributes_from` refuses to change `shop` on a session whose `id` encodes a different shop
