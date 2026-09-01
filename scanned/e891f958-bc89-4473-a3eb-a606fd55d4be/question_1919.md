# Q1919: unified_admin? — validator returns a non-Shopify host via backslash separator

## Question
Starting from the unified-admin branch, entered whenever the first label of the parsed host is literally `admin`, can an unprivileged attacker supply a shop string using a backslash instead of a slash (`https:\\evil.example\admin`), which `Addressable` and HTTParty disagree about so that `sanitize_shop_domain` returns a string that is not a Shopify shop, and that string becomes `@base_uri` in `Clients::HttpClient#initialize`? Determine whether SESSION DERIVATION: a session id is derived only from bytes authenticated under `Context.api_secret_key` still holds through `ShopValidator.unified_admin?`, and whether the result reaches Critical - theft of a merchant's refresh token, granting durable access after rotation.

## Target
- File/function: `lib/shopify_api/utils/shop_validator.rb` -> `ShopValidator.unified_admin?`
- Entrypoint: the unified-admin branch, entered whenever the first label of the parsed host is literally `admin`
- Attacker controls: a shop string using a backslash instead of a slash (`https:\\evil.example\admin`), which `Addressable` and HTTParty disagree about
- Exploit idea: `sanitize_shop_domain` returns a string that is not a Shopify shop, and that string becomes `@base_uri` in `Clients::HttpClient#initialize`
- Invariant to test: SESSION DERIVATION: a session id is derived only from bytes authenticated under `Context.api_secret_key`
- Expected Immunefi impact: Critical - theft of a merchant's refresh token, granting durable access after rotation (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: drive `ClientCredentials.client_credentials(shop: candidate)` under WebMock and assert the request body containing `client_secret` was never sent off-domain
