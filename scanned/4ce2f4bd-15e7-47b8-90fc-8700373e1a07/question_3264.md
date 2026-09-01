# Q3264: auth_base_uri — cookie value becomes the session id via extra query parameters

## Question
Does `Oauth.auth_base_uri` collapse two distinct identities into one when an unprivileged attacker submits additional query keys outside the five that `to_signable_string` covers (`code`, `host`, `shop`, `state`, `timestamp`) at the private `auth_base_uri(shop)` that builds `"https://#{shop}/admin"` with no call to `ShopValidator`? Show that in the non-embedded branch the returned cookie's value is `session.id`, publishing the storage key to the browser, that AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right is violated, and that the consequence is Critical - authentication bypass: a forged or unsigned request is accepted as authentic by the app.

## Target
- File/function: `lib/shopify_api/auth/oauth.rb` -> `Oauth.auth_base_uri`
- Entrypoint: the private `auth_base_uri(shop)` that builds `"https://#{shop}/admin"` with no call to `ShopValidator`
- Attacker controls: additional query keys outside the five that `to_signable_string` covers (`code`, `host`, `shop`, `state`, `timestamp`)
- Exploit idea: in the non-embedded branch the returned cookie's value is `session.id`, publishing the storage key to the browser
- Invariant to test: AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right
- Expected Immunefi impact: Critical - authentication bypass: a forged or unsigned request is accepted as authentic by the app (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest + WebMock: call `begin_auth(shop: 'a.myshopify.com')`, then `validate_auth_callback` with a validly signed query naming shop B, and assert the returned `session.shop`
