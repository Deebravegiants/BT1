# Q4999: uri_from_shop_domain — validator returns a non-Shopify host via dotless name

## Question
Starting from the private `uri_from_shop_domain` normalisation step that downcases, strips, rejects `@` and prepends `https://` before `Addressable::URI.parse`, can an unprivileged attacker supply a dotless shop name that takes the `name += ".#{myshopify_domain}"` branch only when `myshopify_domain` is present, yielding a different verdict for the same input so that `sanitize_shop_domain` returns a string that is not a Shopify shop, and that string becomes `@base_uri` in `Clients::HttpClient#initialize`? Determine whether SESSION DERIVATION: a session id is derived only from bytes authenticated under `Context.api_secret_key` still holds through `ShopValidator.uri_from_shop_domain`, and whether the result reaches Critical - theft of a merchant's refresh token, granting durable access after rotation.

## Target
- File/function: `lib/shopify_api/utils/shop_validator.rb` -> `ShopValidator.uri_from_shop_domain`
- Entrypoint: the private `uri_from_shop_domain` normalisation step that downcases, strips, rejects `@` and prepends `https://` before `Addressable::URI.parse`
- Attacker controls: a dotless shop name that takes the `name += ".#{myshopify_domain}"` branch only when `myshopify_domain` is present, yielding a different verdict for the same input
- Exploit idea: `sanitize_shop_domain` returns a string that is not a Shopify shop, and that string becomes `@base_uri` in `Clients::HttpClient#initialize`
- Invariant to test: SESSION DERIVATION: a session id is derived only from bytes authenticated under `Context.api_secret_key`
- Expected Immunefi impact: Critical - theft of a merchant's refresh token, granting durable access after rotation (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: drive `ClientCredentials.client_credentials(shop: candidate)` under WebMock and assert the request body containing `client_secret` was never sent off-domain
