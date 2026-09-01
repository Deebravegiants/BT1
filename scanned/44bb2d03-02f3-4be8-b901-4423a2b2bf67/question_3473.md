# Q3473: auth_base_uri — no replay window via chosen state cookie

## Question
Starting from the private `auth_base_uri(shop)` that builds `"https://#{shop}/admin"` with no call to `ShopValidator`, can an unprivileged attacker supply the `shopify_app_session` cookie value, set by the attacker in the victim's browser or omitted entirely so that nothing records that a `state` was consumed, so a signed callback can be submitted repeatedly? Determine whether SESSION DERIVATION: a session id is derived only from bytes authenticated under `Context.api_secret_key` still holds through `Oauth.auth_base_uri`, and whether the result reaches Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`).

## Target
- File/function: `lib/shopify_api/auth/oauth.rb` -> `Oauth.auth_base_uri`
- Entrypoint: the private `auth_base_uri(shop)` that builds `"https://#{shop}/admin"` with no call to `ShopValidator`
- Attacker controls: the `shopify_app_session` cookie value, set by the attacker in the victim's browser or omitted entirely
- Exploit idea: nothing records that a `state` was consumed, so a signed callback can be submitted repeatedly
- Invariant to test: SESSION DERIVATION: a session id is derived only from bytes authenticated under `Context.api_secret_key`
- Expected Immunefi impact: Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`) (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert_requested the `/admin/oauth/access_token` POST and check its host equals the shop the browser began with, not the shop in the callback
