# Q3506: auth_base_uri — error path leaks via chosen state cookie

## Question
Is there a reachable state in which an unprivileged attacker, controlling the `shopify_app_session` cookie value, set by the attacker in the victim's browser or omitted entirely at the private `auth_base_uri(shop)` that builds `"https://#{shop}/admin"` with no call to `ShopValidator`, makes `Oauth.auth_base_uri` return a result the caller treats as authenticated, given that `Errors::RequestAccessTokenError` and the HTTParty failure path surface response contents built from a request that carried `client_secret`? Test CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted and quantify High - session fixation / forced OAuth completion binding a victim browser to an attacker-chosen shop.

## Target
- File/function: `lib/shopify_api/auth/oauth.rb` -> `Oauth.auth_base_uri`
- Entrypoint: the private `auth_base_uri(shop)` that builds `"https://#{shop}/admin"` with no call to `ShopValidator`
- Attacker controls: the `shopify_app_session` cookie value, set by the attacker in the victim's browser or omitted entirely
- Exploit idea: `Errors::RequestAccessTokenError` and the HTTParty failure path surface response contents built from a request that carried `client_secret`
- Invariant to test: CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted
- Expected Immunefi impact: High - session fixation / forced OAuth completion binding a victim browser to an attacker-chosen shop (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: replay the same signed `auth_query` twice and assert the second call raises rather than minting a second session
