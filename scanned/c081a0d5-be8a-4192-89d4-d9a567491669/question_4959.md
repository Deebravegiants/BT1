# Q4959: sanitize_shop_domain — shop name reconstructed, not validated via backslash separator

## Question
If an unprivileged attacker submits a shop string using a backslash instead of a slash (`https:\\evil.example\admin`), which `Addressable` and HTTParty disagree about to a host-app route that forwards a user-supplied `shop` query parameter into `ShopifyAPI::Utils::ShopValidator.sanitize_shop_domain`, does `ShopValidator.sanitize_shop_domain` end up acting on a value that was never authenticated, because the returned `"#{shop}.myshopify.com"` is manufactured by string concatenation and never re-validated? Close the question on SESSION DERIVATION: a session id is derived only from bytes authenticated under `Context.api_secret_key` and on Critical - theft of a merchant's refresh token, granting durable access after rotation.

## Target
- File/function: `lib/shopify_api/utils/shop_validator.rb` -> `ShopValidator.sanitize_shop_domain`
- Entrypoint: a host-app route that forwards a user-supplied `shop` query parameter into `ShopifyAPI::Utils::ShopValidator.sanitize_shop_domain`
- Attacker controls: a shop string using a backslash instead of a slash (`https:\\evil.example\admin`), which `Addressable` and HTTParty disagree about
- Exploit idea: the returned `"#{shop}.myshopify.com"` is manufactured by string concatenation and never re-validated
- Invariant to test: SESSION DERIVATION: a session id is derived only from bytes authenticated under `Context.api_secret_key`
- Expected Immunefi impact: Critical - theft of a merchant's refresh token, granting durable access after rotation (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: drive `ClientCredentials.client_credentials(shop: candidate)` under WebMock and assert the request body containing `client_secret` was never sent off-domain
