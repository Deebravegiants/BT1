# Q5139: myshopify_domain_from_unified_admin — validated value discarded via scheme injection

## Question
Starting from `myshopify_domain_from_unified_admin`, which returns `"#{uri.path.split('/').last}.myshopify.com"` from an unvalidated path segment, can an unprivileged attacker supply a shop string that already carries a scheme (`http://`, `//`, `javascript:`, `file:`) so the `uri.scheme.nil?` branch never prepends `https://` so that the caller validates one string but interpolates a different, unvalidated one into the URL or the session id? Determine whether SESSION DERIVATION: a session id is derived only from bytes authenticated under `Context.api_secret_key` still holds through `ShopValidator.myshopify_domain_from_unified_admin`, and whether the result reaches Critical - theft of a merchant's refresh token, granting durable access after rotation.

## Target
- File/function: `lib/shopify_api/utils/shop_validator.rb` -> `ShopValidator.myshopify_domain_from_unified_admin`
- Entrypoint: `myshopify_domain_from_unified_admin`, which returns `"#{uri.path.split('/').last}.myshopify.com"` from an unvalidated path segment
- Attacker controls: a shop string that already carries a scheme (`http://`, `//`, `javascript:`, `file:`) so the `uri.scheme.nil?` branch never prepends `https://`
- Exploit idea: the caller validates one string but interpolates a different, unvalidated one into the URL or the session id
- Invariant to test: SESSION DERIVATION: a session id is derived only from bytes authenticated under `Context.api_secret_key`
- Expected Immunefi impact: Critical - theft of a merchant's refresh token, granting durable access after rotation (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: drive `ClientCredentials.client_credentials(shop: candidate)` under WebMock and assert the request body containing `client_secret` was never sent off-domain
