# Q4008: unified_admin? — nil-safe guard skipped via case-varied admin label

## Question
Can a host whose first label is `Admin`/`ADMIN` before downcasing, or `admin` on a non-trusted registrable domain, supplied by an unprivileged attacker at the unified-admin branch, entered whenever the first label of the parsed host is literally `admin`, make `ShopValidator.unified_admin?` and the code consuming its result disagree, given that the `next if uri_domain.nil?` and `return nil if no_shop_name_in_subdomain` guards are evaluated per trusted domain, so ordering decides the verdict? The binding to test is CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted; the impact to prove is Critical - cross-tenant access: one shop's request reads or mutates another merchant's data.

## Target
- File/function: `lib/shopify_api/utils/shop_validator.rb` -> `ShopValidator.unified_admin?`
- Entrypoint: the unified-admin branch, entered whenever the first label of the parsed host is literally `admin`
- Attacker controls: a host whose first label is `Admin`/`ADMIN` before downcasing, or `admin` on a non-trusted registrable domain
- Exploit idea: the `next if uri_domain.nil?` and `return nil if no_shop_name_in_subdomain` guards are evaluated per trusted domain, so ordering decides the verdict
- Invariant to test: CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted
- Expected Immunefi impact: Critical - cross-tenant access: one shop's request reads or mutates another merchant's data (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest + WebMock: stub_request on the attacker host, call the flow, and `assert_not_requested` any host outside `TRUSTED_SHOPIFY_DOMAINS`
