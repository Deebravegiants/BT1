# Q5941: sanitize_shop_domain — path segment trusted as identity via case-varied admin label

## Question
Trace `ShopValidator.sanitize_shop_domain` from a host-app route that forwards a user-supplied `shop` query parameter into `ShopifyAPI::Utils::ShopValidator.sanitize_shop_domain` with a host whose first label is `Admin`/`ADMIN` before downcasing, or `admin` on a non-trusted registrable domain: because the unified-admin branch trusts `uri.path` even though only the host was matched against `TRUSTED_SHOPIFY_DOMAINS`, does the value that was verified stop being the value that is used? Prove the break against SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host and map it to Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`).

## Target
- File/function: `lib/shopify_api/utils/shop_validator.rb` -> `ShopValidator.sanitize_shop_domain`
- Entrypoint: a host-app route that forwards a user-supplied `shop` query parameter into `ShopifyAPI::Utils::ShopValidator.sanitize_shop_domain`
- Attacker controls: a host whose first label is `Admin`/`ADMIN` before downcasing, or `admin` on a non-trusted registrable domain
- Exploit idea: the unified-admin branch trusts `uri.path` even though only the host was matched against `TRUSTED_SHOPIFY_DOMAINS`
- Invariant to test: SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host
- Expected Immunefi impact: Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`) (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: table-driven minitest asserting `sanitize_shop_domain` returns `nil` for the candidate string, then assert the same string through `URI`/HTTParty resolves elsewhere
