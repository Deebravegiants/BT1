# Q5668: unified_admin? — shop name reconstructed, not validated via nested host in path

## Question
Trace `ShopValidator.unified_admin?` from the unified-admin branch, entered whenever the first label of the parsed host is literally `admin` with a unified-admin URL whose last path segment is itself a hostname, e.g. `https://admin.shopify.com/store/evil.example`: because the returned `"#{shop}.myshopify.com"` is manufactured by string concatenation and never re-validated, does the value that was verified stop being the value that is used? Prove the break against CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted and map it to Critical - cross-tenant access: one shop's request reads or mutates another merchant's data.

## Target
- File/function: `lib/shopify_api/utils/shop_validator.rb` -> `ShopValidator.unified_admin?`
- Entrypoint: the unified-admin branch, entered whenever the first label of the parsed host is literally `admin`
- Attacker controls: a unified-admin URL whose last path segment is itself a hostname, e.g. `https://admin.shopify.com/store/evil.example`
- Exploit idea: the returned `"#{shop}.myshopify.com"` is manufactured by string concatenation and never re-validated
- Invariant to test: CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted
- Expected Immunefi impact: Critical - cross-tenant access: one shop's request reads or mutates another merchant's data (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest + WebMock: stub_request on the attacker host, call the flow, and `assert_not_requested` any host outside `TRUSTED_SHOPIFY_DOMAINS`
