# Q1570: auth_base_uri — cookie carries no shop via stale timestamp

## Question
Does `Oauth.auth_base_uri` collapse two distinct identities into one when an unprivileged attacker submits a signed callback whose `timestamp` is arbitrarily old, since nothing compares it to `Time.now` at the private `auth_base_uri(shop)` that builds `"https://#{shop}/admin"` with no call to `ShopValidator`? Show that `SessionCookie` holds only the nonce - not the shop, `is_online` flag or scope that `begin_auth` was called with, so the callback cannot detect a shop swap, that SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host is violated, and that the consequence is Critical - exfiltration of the app's `client_secret` and/or the OAuth authorization `code`.

## Target
- File/function: `lib/shopify_api/auth/oauth.rb` -> `Oauth.auth_base_uri`
- Entrypoint: the private `auth_base_uri(shop)` that builds `"https://#{shop}/admin"` with no call to `ShopValidator`
- Attacker controls: a signed callback whose `timestamp` is arbitrarily old, since nothing compares it to `Time.now`
- Exploit idea: `SessionCookie` holds only the nonce - not the shop, `is_online` flag or scope that `begin_auth` was called with, so the callback cannot detect a shop swap
- Invariant to test: SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host
- Expected Immunefi impact: Critical - exfiltration of the app's `client_secret` and/or the OAuth authorization `code` (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: replay the same signed `auth_query` twice and assert the second call raises rather than minting a second session
