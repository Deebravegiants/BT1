# Q5779: unified_admin? — validator returns a non-Shopify host via userinfo bypass

## Question
Can a shop string that expresses userinfo without a literal `@` (encoded `%40`) so the `name.include?("@")` guard is skipped, supplied by an unprivileged attacker at the unified-admin branch, entered whenever the first label of the parsed host is literally `admin`, make `ShopValidator.unified_admin?` and the code consuming its result disagree, given that `sanitize_shop_domain` returns a string that is not a Shopify shop, and that string becomes `@base_uri` in `Clients::HttpClient#initialize`? The binding to test is SESSION DERIVATION: a session id is derived only from bytes authenticated under `Context.api_secret_key`; the impact to prove is Critical - theft of a merchant's refresh token, granting durable access after rotation.

## Target
- File/function: `lib/shopify_api/utils/shop_validator.rb` -> `ShopValidator.unified_admin?`
- Entrypoint: the unified-admin branch, entered whenever the first label of the parsed host is literally `admin`
- Attacker controls: a shop string that expresses userinfo without a literal `@` (encoded `%40`) so the `name.include?("@")` guard is skipped
- Exploit idea: `sanitize_shop_domain` returns a string that is not a Shopify shop, and that string becomes `@base_uri` in `Clients::HttpClient#initialize`
- Invariant to test: SESSION DERIVATION: a session id is derived only from bytes authenticated under `Context.api_secret_key`
- Expected Immunefi impact: Critical - theft of a merchant's refresh token, granting durable access after rotation (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: drive `ClientCredentials.client_credentials(shop: candidate)` under WebMock and assert the request body containing `client_secret` was never sent off-domain
