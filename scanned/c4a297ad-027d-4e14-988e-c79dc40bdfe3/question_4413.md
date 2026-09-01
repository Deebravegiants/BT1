# Q4413: validate_auth_callback — cookie value becomes the session id via unsanitised shop param

## Question
If an unprivileged attacker submits the `shop` query parameter, which neither `begin_auth` nor `validate_auth_callback` passes through `ShopValidator.sanitize!` to `ShopifyAPI::Auth::Oauth.validate_auth_callback(cookies:, auth_query:)`, reached from the app's public OAuth callback route, does `Oauth.validate_auth_callback` end up acting on a value that was never authenticated, because in the non-embedded branch the returned cookie's value is `session.id`, publishing the storage key to the browser? Close the question on SESSION DERIVATION: a session id is derived only from bytes authenticated under `Context.api_secret_key` and on Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`).

## Target
- File/function: `lib/shopify_api/auth/oauth.rb` -> `Oauth.validate_auth_callback`
- Entrypoint: `ShopifyAPI::Auth::Oauth.validate_auth_callback(cookies:, auth_query:)`, reached from the app's public OAuth callback route
- Attacker controls: the `shop` query parameter, which neither `begin_auth` nor `validate_auth_callback` passes through `ShopValidator.sanitize!`
- Exploit idea: in the non-embedded branch the returned cookie's value is `session.id`, publishing the storage key to the browser
- Invariant to test: SESSION DERIVATION: a session id is derived only from bytes authenticated under `Context.api_secret_key`
- Expected Immunefi impact: Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`) (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert_requested the `/admin/oauth/access_token` POST and check its host equals the shop the browser began with, not the shop in the callback
