# Q2610: auth_base_uri — HMAC precedes but does not bind via empty state

## Question
Is there a reachable state in which an unprivileged attacker, controlling an empty-string `state` in both cookie and query, so the `state == auth_query.state` comparison trivially succeeds at the private `auth_base_uri(shop)` that builds `"https://#{shop}/admin"` with no call to `ShopValidator`, makes `Oauth.auth_base_uri` return a result the caller treats as authenticated, given that `HmacValidator.validate(auth_query)` proves Shopify signed those five fields, not that this browser began this authorization? Test SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host and quantify Critical - exfiltration of the app's `client_secret` and/or the OAuth authorization `code`.

## Target
- File/function: `lib/shopify_api/auth/oauth.rb` -> `Oauth.auth_base_uri`
- Entrypoint: the private `auth_base_uri(shop)` that builds `"https://#{shop}/admin"` with no call to `ShopValidator`
- Attacker controls: an empty-string `state` in both cookie and query, so the `state == auth_query.state` comparison trivially succeeds
- Exploit idea: `HmacValidator.validate(auth_query)` proves Shopify signed those five fields, not that this browser began this authorization
- Invariant to test: SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host
- Expected Immunefi impact: Critical - exfiltration of the app's `client_secret` and/or the OAuth authorization `code` (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: replay the same signed `auth_query` twice and assert the second call raises rather than minting a second session
