# Q4824: myshopify_domain_from_unified_admin — nil-safe guard skipped via percent-encoded separator

## Question
Starting from `myshopify_domain_from_unified_admin`, which returns `"#{uri.path.split('/').last}.myshopify.com"` from an unvalidated path segment, can an unprivileged attacker supply a shop string with percent-encoded path/host separators such as `admin.shopify.com%2Fstore%2Fvictim` or `%2e%2e` segments so that the `next if uri_domain.nil?` and `return nil if no_shop_name_in_subdomain` guards are evaluated per trusted domain, so ordering decides the verdict? Determine whether CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted still holds through `ShopValidator.myshopify_domain_from_unified_admin`, and whether the result reaches Critical - theft of a merchant's refresh token, granting durable access after rotation.

## Target
- File/function: `lib/shopify_api/utils/shop_validator.rb` -> `ShopValidator.myshopify_domain_from_unified_admin`
- Entrypoint: `myshopify_domain_from_unified_admin`, which returns `"#{uri.path.split('/').last}.myshopify.com"` from an unvalidated path segment
- Attacker controls: a shop string with percent-encoded path/host separators such as `admin.shopify.com%2Fstore%2Fvictim` or `%2e%2e` segments
- Exploit idea: the `next if uri_domain.nil?` and `return nil if no_shop_name_in_subdomain` guards are evaluated per trusted domain, so ordering decides the verdict
- Invariant to test: CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted
- Expected Immunefi impact: Critical - theft of a merchant's refresh token, granting durable access after rotation (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest + WebMock: stub_request on the attacker host, call the flow, and `assert_not_requested` any host outside `TRUSTED_SHOPIFY_DOMAINS`
