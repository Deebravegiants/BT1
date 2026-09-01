# Q5029: myshopify_domain_from_unified_admin — dev-domain entries reachable in production via percent-encoded separator

## Question
If an unprivileged attacker submits a shop string with percent-encoded path/host separators such as `admin.shopify.com%2Fstore%2Fvictim` or `%2e%2e` segments to `myshopify_domain_from_unified_admin`, which returns `"#{uri.path.split('/').last}.myshopify.com"` from an unvalidated path segment, does `ShopValidator.myshopify_domain_from_unified_admin` end up acting on a value that was never authenticated, because `spin.dev` and `shop.dev` remain in `TRUSTED_SHOPIFY_DOMAINS` in production builds and are registrable by third parties? Close the question on SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host and on Critical - theft of a merchant's refresh token, granting durable access after rotation.

## Target
- File/function: `lib/shopify_api/utils/shop_validator.rb` -> `ShopValidator.myshopify_domain_from_unified_admin`
- Entrypoint: `myshopify_domain_from_unified_admin`, which returns `"#{uri.path.split('/').last}.myshopify.com"` from an unvalidated path segment
- Attacker controls: a shop string with percent-encoded path/host separators such as `admin.shopify.com%2Fstore%2Fvictim` or `%2e%2e` segments
- Exploit idea: `spin.dev` and `shop.dev` remain in `TRUSTED_SHOPIFY_DOMAINS` in production builds and are registrable by third parties
- Invariant to test: SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host
- Expected Immunefi impact: Critical - theft of a merchant's refresh token, granting durable access after rotation (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: table-driven minitest asserting `sanitize_shop_domain` returns `nil` for the candidate string, then assert the same string through `URI`/HTTParty resolves elsewhere
