# Q3066: auth_base_uri — private-app guard ordering via cross-shop state reuse

## Question
Can an unprivileged attacker reach `Oauth.auth_base_uri` through the private `auth_base_uri(shop)` that builds `"https://#{shop}/admin"` with no call to `ShopValidator` while supplying a `state` nonce obtained from the attacker's own `begin_auth` call and presented with a callback naming a different `shop`, so that `Context.private?` and `Context.setup?` are checked around, not before, the value that decides the outbound host, breaking the requirement that CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted, and ending in High - session fixation / forced OAuth completion binding a victim browser to an attacker-chosen shop?

## Target
- File/function: `lib/shopify_api/auth/oauth.rb` -> `Oauth.auth_base_uri`
- Entrypoint: the private `auth_base_uri(shop)` that builds `"https://#{shop}/admin"` with no call to `ShopValidator`
- Attacker controls: a `state` nonce obtained from the attacker's own `begin_auth` call and presented with a callback naming a different `shop`
- Exploit idea: `Context.private?` and `Context.setup?` are checked around, not before, the value that decides the outbound host
- Invariant to test: CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted
- Expected Immunefi impact: High - session fixation / forced OAuth completion binding a victim browser to an attacker-chosen shop (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: replay the same signed `auth_query` twice and assert the second call raises rather than minting a second session
