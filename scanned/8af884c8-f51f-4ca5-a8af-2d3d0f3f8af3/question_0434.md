# Q434: auth_base_uri — cookie carries no shop via duplicated query keys

## Question
Can an unprivileged attacker reach `Oauth.auth_base_uri` through the private `auth_base_uri(shop)` that builds `"https://#{shop}/admin"` with no call to `ShopValidator` while supplying repeated `shop=`/`state=` keys where the framework's last-wins parse differs from the value that was signed, so that `SessionCookie` holds only the nonce - not the shop, `is_online` flag or scope that `begin_auth` was called with, so the callback cannot detect a shop swap, breaking the requirement that AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right, and ending in Critical - authentication bypass: a forged or unsigned request is accepted as authentic by the app?

## Target
- File/function: `lib/shopify_api/auth/oauth.rb` -> `Oauth.auth_base_uri`
- Entrypoint: the private `auth_base_uri(shop)` that builds `"https://#{shop}/admin"` with no call to `ShopValidator`
- Attacker controls: repeated `shop=`/`state=` keys where the framework's last-wins parse differs from the value that was signed
- Exploit idea: `SessionCookie` holds only the nonce - not the shop, `is_online` flag or scope that `begin_auth` was called with, so the callback cannot detect a shop swap
- Invariant to test: AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right
- Expected Immunefi impact: Critical - authentication bypass: a forged or unsigned request is accepted as authentic by the app (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: replay the same signed `auth_query` twice and assert the second call raises rather than minting a second session
