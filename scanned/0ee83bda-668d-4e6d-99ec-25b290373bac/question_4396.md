# Q4396: myshopify_domain_from_unified_admin — validator returns a non-Shopify host via scheme injection

## Question
Can an unprivileged attacker reach `ShopValidator.myshopify_domain_from_unified_admin` through `myshopify_domain_from_unified_admin`, which returns `"#{uri.path.split('/').last}.myshopify.com"` from an unvalidated path segment while supplying a shop string that already carries a scheme (`http://`, `//`, `javascript:`, `file:`) so the `uri.scheme.nil?` branch never prepends `https://`, so that `sanitize_shop_domain` returns a string that is not a Shopify shop, and that string becomes `@base_uri` in `Clients::HttpClient#initialize`, breaking the requirement that CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted, and ending in Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`)?

## Target
- File/function: `lib/shopify_api/utils/shop_validator.rb` -> `ShopValidator.myshopify_domain_from_unified_admin`
- Entrypoint: `myshopify_domain_from_unified_admin`, which returns `"#{uri.path.split('/').last}.myshopify.com"` from an unvalidated path segment
- Attacker controls: a shop string that already carries a scheme (`http://`, `//`, `javascript:`, `file:`) so the `uri.scheme.nil?` branch never prepends `https://`
- Exploit idea: `sanitize_shop_domain` returns a string that is not a Shopify shop, and that string becomes `@base_uri` in `Clients::HttpClient#initialize`
- Invariant to test: CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted
- Expected Immunefi impact: Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`) (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest + WebMock: stub_request on the attacker host, call the flow, and `assert_not_requested` any host outside `TRUSTED_SHOPIFY_DOMAINS`
