# Q5803: myshopify_domain_from_unified_admin — dev-domain entries reachable in production via nested host in path

## Question
Can an unprivileged attacker reach `ShopValidator.myshopify_domain_from_unified_admin` through `myshopify_domain_from_unified_admin`, which returns `"#{uri.path.split('/').last}.myshopify.com"` from an unvalidated path segment while supplying a unified-admin URL whose last path segment is itself a hostname, e.g. `https://admin.shopify.com/store/evil.example`, so that `spin.dev` and `shop.dev` remain in `TRUSTED_SHOPIFY_DOMAINS` in production builds and are registrable by third parties, breaking the requirement that SESSION DERIVATION: a session id is derived only from bytes authenticated under `Context.api_secret_key`, and ending in Critical - cross-tenant access: one shop's request reads or mutates another merchant's data?

## Target
- File/function: `lib/shopify_api/utils/shop_validator.rb` -> `ShopValidator.myshopify_domain_from_unified_admin`
- Entrypoint: `myshopify_domain_from_unified_admin`, which returns `"#{uri.path.split('/').last}.myshopify.com"` from an unvalidated path segment
- Attacker controls: a unified-admin URL whose last path segment is itself a hostname, e.g. `https://admin.shopify.com/store/evil.example`
- Exploit idea: `spin.dev` and `shop.dev` remain in `TRUSTED_SHOPIFY_DOMAINS` in production builds and are registrable by third parties
- Invariant to test: SESSION DERIVATION: a session id is derived only from bytes authenticated under `Context.api_secret_key`
- Expected Immunefi impact: Critical - cross-tenant access: one shop's request reads or mutates another merchant's data (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: drive `ClientCredentials.client_credentials(shop: candidate)` under WebMock and assert the request body containing `client_secret` was never sent off-domain
