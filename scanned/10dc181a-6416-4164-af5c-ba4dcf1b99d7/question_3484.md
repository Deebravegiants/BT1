# Q3484: validate_auth_callback — cookie value becomes the session id via cross-shop state reuse

## Question
Trace `Oauth.validate_auth_callback` from `ShopifyAPI::Auth::Oauth.validate_auth_callback(cookies:, auth_query:)`, reached from the app's public OAuth callback route with a `state` nonce obtained from the attacker's own `begin_auth` call and presented with a callback naming a different `shop`: because in the non-embedded branch the returned cookie's value is `session.id`, publishing the storage key to the browser, does the value that was verified stop being the value that is used? Prove the break against AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right and map it to Critical - authentication bypass: a forged or unsigned request is accepted as authentic by the app.

## Target
- File/function: `lib/shopify_api/auth/oauth.rb` -> `Oauth.validate_auth_callback`
- Entrypoint: `ShopifyAPI::Auth::Oauth.validate_auth_callback(cookies:, auth_query:)`, reached from the app's public OAuth callback route
- Attacker controls: a `state` nonce obtained from the attacker's own `begin_auth` call and presented with a callback naming a different `shop`
- Exploit idea: in the non-embedded branch the returned cookie's value is `session.id`, publishing the storage key to the browser
- Invariant to test: AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right
- Expected Immunefi impact: Critical - authentication bypass: a forged or unsigned request is accepted as authentic by the app (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest + WebMock: call `begin_auth(shop: 'a.myshopify.com')`, then `validate_auth_callback` with a validly signed query naming shop B, and assert the returned `session.shop`
