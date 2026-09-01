# Q3439: myshopify_domain_from_unified_admin — nil-safe guard skipped via scheme injection

## Question
Does `ShopValidator.myshopify_domain_from_unified_admin` collapse two distinct identities into one when an unprivileged attacker submits a shop string that already carries a scheme (`http://`, `//`, `javascript:`, `file:`) so the `uri.scheme.nil?` branch never prepends `https://` at `myshopify_domain_from_unified_admin`, which returns `"#{uri.path.split('/').last}.myshopify.com"` from an unvalidated path segment? Show that the `next if uri_domain.nil?` and `return nil if no_shop_name_in_subdomain` guards are evaluated per trusted domain, so ordering decides the verdict, that SESSION DERIVATION: a session id is derived only from bytes authenticated under `Context.api_secret_key` is violated, and that the consequence is Critical - theft of a merchant's refresh token, granting durable access after rotation.

## Target
- File/function: `lib/shopify_api/utils/shop_validator.rb` -> `ShopValidator.myshopify_domain_from_unified_admin`
- Entrypoint: `myshopify_domain_from_unified_admin`, which returns `"#{uri.path.split('/').last}.myshopify.com"` from an unvalidated path segment
- Attacker controls: a shop string that already carries a scheme (`http://`, `//`, `javascript:`, `file:`) so the `uri.scheme.nil?` branch never prepends `https://`
- Exploit idea: the `next if uri_domain.nil?` and `return nil if no_shop_name_in_subdomain` guards are evaluated per trusted domain, so ordering decides the verdict
- Invariant to test: SESSION DERIVATION: a session id is derived only from bytes authenticated under `Context.api_secret_key`
- Expected Immunefi impact: Critical - theft of a merchant's refresh token, granting durable access after rotation (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: drive `ClientCredentials.client_credentials(shop: candidate)` under WebMock and assert the request body containing `client_secret` was never sent off-domain
