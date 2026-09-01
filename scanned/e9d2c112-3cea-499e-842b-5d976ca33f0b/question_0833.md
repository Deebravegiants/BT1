# Q833: auth_base_uri — redirect target unbound via unsanitised shop param

## Question
Can an unprivileged attacker reach `Oauth.auth_base_uri` through the private `auth_base_uri(shop)` that builds `"https://#{shop}/admin"` with no call to `ShopValidator` while supplying the `shop` query parameter, which neither `begin_auth` nor `validate_auth_callback` passes through `ShopValidator.sanitize!`, so that `redirect_uri` is built from `Context.host` + `redirect_path` at authorize time but never re-verified at callback time, breaking the requirement that SESSION DERIVATION: a session id is derived only from bytes authenticated under `Context.api_secret_key`, and ending in Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`)?

## Target
- File/function: `lib/shopify_api/auth/oauth.rb` -> `Oauth.auth_base_uri`
- Entrypoint: the private `auth_base_uri(shop)` that builds `"https://#{shop}/admin"` with no call to `ShopValidator`
- Attacker controls: the `shop` query parameter, which neither `begin_auth` nor `validate_auth_callback` passes through `ShopValidator.sanitize!`
- Exploit idea: `redirect_uri` is built from `Context.host` + `redirect_path` at authorize time but never re-verified at callback time
- Invariant to test: SESSION DERIVATION: a session id is derived only from bytes authenticated under `Context.api_secret_key`
- Expected Immunefi impact: Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`) (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert_requested the `/admin/oauth/access_token` POST and check its host equals the shop the browser began with, not the shop in the callback
