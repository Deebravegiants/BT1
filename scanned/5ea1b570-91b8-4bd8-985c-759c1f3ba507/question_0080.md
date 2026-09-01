# Q80: auth_base_uri — no replay window via unsanitised shop param

## Question
If an unprivileged attacker submits the `shop` query parameter, which neither `begin_auth` nor `validate_auth_callback` passes through `ShopValidator.sanitize!` to the private `auth_base_uri(shop)` that builds `"https://#{shop}/admin"` with no call to `ShopValidator`, does `Oauth.auth_base_uri` end up acting on a value that was never authenticated, because nothing records that a `state` was consumed, so a signed callback can be submitted repeatedly? Close the question on SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host and on Critical - exfiltration of the app's `client_secret` and/or the OAuth authorization `code`.

## Target
- File/function: `lib/shopify_api/auth/oauth.rb` -> `Oauth.auth_base_uri`
- Entrypoint: the private `auth_base_uri(shop)` that builds `"https://#{shop}/admin"` with no call to `ShopValidator`
- Attacker controls: the `shop` query parameter, which neither `begin_auth` nor `validate_auth_callback` passes through `ShopValidator.sanitize!`
- Exploit idea: nothing records that a `state` was consumed, so a signed callback can be submitted repeatedly
- Invariant to test: SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host
- Expected Immunefi impact: Critical - exfiltration of the app's `client_secret` and/or the OAuth authorization `code` (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest + WebMock: call `begin_auth(shop: 'a.myshopify.com')`, then `validate_auth_callback` with a validly signed query naming shop B, and assert the returned `session.shop`
