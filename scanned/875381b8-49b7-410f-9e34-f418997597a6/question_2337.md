# Q2337: from — temp restores unconditionally via nil expires

## Question
Is there a reachable state in which an unprivileged attacker, controlling an access-token response with no `expires_in`, leaving `@expires` nil and `expired?` permanently false at `Session.from(shop:, access_token_response:)`, which mints `"#{shop}_#{associated_user.id}"` or `"offline_#{shop}"`, makes `Auth::Session.from` return a result the caller treats as authenticated, given that the `ensure` block restores whatever was captured, which under nesting or threading may not be the caller's session? Test SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host and quantify Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`).

## Target
- File/function: `lib/shopify_api/auth/session.rb` -> `Auth::Session.from`
- Entrypoint: `Session.from(shop:, access_token_response:)`, which mints `"#{shop}_#{associated_user.id}"` or `"offline_#{shop}"`
- Attacker controls: an access-token response with no `expires_in`, leaving `@expires` nil and `expired?` permanently false
- Exploit idea: the `ensure` block restores whatever was captured, which under nesting or threading may not be the caller's session
- Invariant to test: SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host
- Expected Immunefi impact: Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`) (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest: construct sessions for shops containing `_` and assert `Session.from` ids are injective across (shop, user) pairs
