# Q4974: sanitize_shop_domain — trusted list widened per call via trailing-dot host

## Question
Can a shop string with a fully-qualified trailing dot such as `victim.myshopify.com.` so that the parsed `domain` and the host an HTTP client actually resolves differ, supplied by an unprivileged attacker at a host-app route that forwards a user-supplied `shop` query parameter into `ShopifyAPI::Utils::ShopValidator.sanitize_shop_domain`, make `ShopValidator.sanitize_shop_domain` and the code consuming its result disagree, given that `trusted_domains` mutates a dup of the constant with a caller-supplied value, so the trust set is request-scoped? The binding to test is SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source; the impact to prove is Critical - theft of a merchant's refresh token, granting durable access after rotation.

## Target
- File/function: `lib/shopify_api/utils/shop_validator.rb` -> `ShopValidator.sanitize_shop_domain`
- Entrypoint: a host-app route that forwards a user-supplied `shop` query parameter into `ShopifyAPI::Utils::ShopValidator.sanitize_shop_domain`
- Attacker controls: a shop string with a fully-qualified trailing dot such as `victim.myshopify.com.` so that the parsed `domain` and the host an HTTP client actually resolves differ
- Exploit idea: `trusted_domains` mutates a dup of the constant with a caller-supplied value, so the trust set is request-scoped
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: Critical - theft of a merchant's refresh token, granting durable access after rotation (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `sanitize!` raises `Errors::InvalidShopError` for the input; if it returns, print the value and diff it against the host in the recorded WebMock request
