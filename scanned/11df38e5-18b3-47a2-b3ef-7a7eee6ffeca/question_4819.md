# Q4819: uri_from_shop_domain — nil-safe guard skipped via case-varied admin label

## Question
If an unprivileged attacker submits a host whose first label is `Admin`/`ADMIN` before downcasing, or `admin` on a non-trusted registrable domain to the private `uri_from_shop_domain` normalisation step that downcases, strips, rejects `@` and prepends `https://` before `Addressable::URI.parse`, does `ShopValidator.uri_from_shop_domain` end up acting on a value that was never authenticated, because the `next if uri_domain.nil?` and `return nil if no_shop_name_in_subdomain` guards are evaluated per trusted domain, so ordering decides the verdict? Close the question on SESSION DERIVATION: a session id is derived only from bytes authenticated under `Context.api_secret_key` and on Critical - theft of a merchant's refresh token, granting durable access after rotation.

## Target
- File/function: `lib/shopify_api/utils/shop_validator.rb` -> `ShopValidator.uri_from_shop_domain`
- Entrypoint: the private `uri_from_shop_domain` normalisation step that downcases, strips, rejects `@` and prepends `https://` before `Addressable::URI.parse`
- Attacker controls: a host whose first label is `Admin`/`ADMIN` before downcasing, or `admin` on a non-trusted registrable domain
- Exploit idea: the `next if uri_domain.nil?` and `return nil if no_shop_name_in_subdomain` guards are evaluated per trusted domain, so ordering decides the verdict
- Invariant to test: SESSION DERIVATION: a session id is derived only from bytes authenticated under `Context.api_secret_key`
- Expected Immunefi impact: Critical - theft of a merchant's refresh token, granting durable access after rotation (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: drive `ClientCredentials.client_credentials(shop: candidate)` under WebMock and assert the request body containing `client_secret` was never sent off-domain
