# Q4219: uri_from_shop_domain — parse/resolve divergence via userinfo bypass

## Question
Trace `ShopValidator.uri_from_shop_domain` from the private `uri_from_shop_domain` normalisation step that downcases, strips, rejects `@` and prepends `https://` before `Addressable::URI.parse` with a shop string that expresses userinfo without a literal `@` (encoded `%40`) so the `name.include?("@")` guard is skipped: because what `Addressable::URI` reports as `host`/`domain` differs from the authority HTTParty finally connects to, does the value that was verified stop being the value that is used? Prove the break against SESSION DERIVATION: a session id is derived only from bytes authenticated under `Context.api_secret_key` and map it to Critical - theft of a merchant's refresh token, granting durable access after rotation.

## Target
- File/function: `lib/shopify_api/utils/shop_validator.rb` -> `ShopValidator.uri_from_shop_domain`
- Entrypoint: the private `uri_from_shop_domain` normalisation step that downcases, strips, rejects `@` and prepends `https://` before `Addressable::URI.parse`
- Attacker controls: a shop string that expresses userinfo without a literal `@` (encoded `%40`) so the `name.include?("@")` guard is skipped
- Exploit idea: what `Addressable::URI` reports as `host`/`domain` differs from the authority HTTParty finally connects to
- Invariant to test: SESSION DERIVATION: a session id is derived only from bytes authenticated under `Context.api_secret_key`
- Expected Immunefi impact: Critical - theft of a merchant's refresh token, granting durable access after rotation (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: drive `ClientCredentials.client_credentials(shop: candidate)` under WebMock and assert the request body containing `client_secret` was never sent off-domain
