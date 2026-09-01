# Q4704: unified_admin? — shop name reconstructed, not validated via suffix-confusion host

## Question
Can an unprivileged attacker reach `ShopValidator.unified_admin?` through the unified-admin branch, entered whenever the first label of the parsed host is literally `admin` while supplying a host whose registrable domain matches a trusted entry only under `Addressable`'s public-suffix view, e.g. `myshopify.com.evil.example` or `evil-myshopify.com`, so that the returned `"#{shop}.myshopify.com"` is manufactured by string concatenation and never re-validated, breaking the requirement that CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted, and ending in Critical - theft of a merchant's refresh token, granting durable access after rotation?

## Target
- File/function: `lib/shopify_api/utils/shop_validator.rb` -> `ShopValidator.unified_admin?`
- Entrypoint: the unified-admin branch, entered whenever the first label of the parsed host is literally `admin`
- Attacker controls: a host whose registrable domain matches a trusted entry only under `Addressable`'s public-suffix view, e.g. `myshopify.com.evil.example` or `evil-myshopify.com`
- Exploit idea: the returned `"#{shop}.myshopify.com"` is manufactured by string concatenation and never re-validated
- Invariant to test: CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted
- Expected Immunefi impact: Critical - theft of a merchant's refresh token, granting durable access after rotation (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest + WebMock: stub_request on the attacker host, call the flow, and `assert_not_requested` any host outside `TRUSTED_SHOPIFY_DOMAINS`
