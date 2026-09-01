# Q5174: sanitize_shop_domain — shop name reconstructed, not validated via scheme injection

## Question
Starting from a host-app route that forwards a user-supplied `shop` query parameter into `ShopifyAPI::Utils::ShopValidator.sanitize_shop_domain`, can an unprivileged attacker supply a shop string that already carries a scheme (`http://`, `//`, `javascript:`, `file:`) so the `uri.scheme.nil?` branch never prepends `https://` so that the returned `"#{shop}.myshopify.com"` is manufactured by string concatenation and never re-validated? Determine whether SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source still holds through `ShopValidator.sanitize_shop_domain`, and whether the result reaches Critical - theft of a merchant's refresh token, granting durable access after rotation.

## Target
- File/function: `lib/shopify_api/utils/shop_validator.rb` -> `ShopValidator.sanitize_shop_domain`
- Entrypoint: a host-app route that forwards a user-supplied `shop` query parameter into `ShopifyAPI::Utils::ShopValidator.sanitize_shop_domain`
- Attacker controls: a shop string that already carries a scheme (`http://`, `//`, `javascript:`, `file:`) so the `uri.scheme.nil?` branch never prepends `https://`
- Exploit idea: the returned `"#{shop}.myshopify.com"` is manufactured by string concatenation and never re-validated
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: Critical - theft of a merchant's refresh token, granting durable access after rotation (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `sanitize!` raises `Errors::InvalidShopError` for the input; if it returns, print the value and diff it against the host in the recorded WebMock request
