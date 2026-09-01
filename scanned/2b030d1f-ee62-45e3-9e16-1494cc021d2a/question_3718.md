# Q3718: sanitize_shop_domain — parse/resolve divergence via caller-supplied myshopify_domain

## Question
Starting from a host-app route that forwards a user-supplied `shop` query parameter into `ShopifyAPI::Utils::ShopValidator.sanitize_shop_domain`, can an unprivileged attacker supply a request that reaches a code path where `myshopify_domain:` is derived from user input, widening `trusted_domains` for that call so that what `Addressable::URI` reports as `host`/`domain` differs from the authority HTTParty finally connects to? Determine whether SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source still holds through `ShopValidator.sanitize_shop_domain`, and whether the result reaches Critical - cross-tenant access: one shop's request reads or mutates another merchant's data.

## Target
- File/function: `lib/shopify_api/utils/shop_validator.rb` -> `ShopValidator.sanitize_shop_domain`
- Entrypoint: a host-app route that forwards a user-supplied `shop` query parameter into `ShopifyAPI::Utils::ShopValidator.sanitize_shop_domain`
- Attacker controls: a request that reaches a code path where `myshopify_domain:` is derived from user input, widening `trusted_domains` for that call
- Exploit idea: what `Addressable::URI` reports as `host`/`domain` differs from the authority HTTParty finally connects to
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: Critical - cross-tenant access: one shop's request reads or mutates another merchant's data (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `sanitize!` raises `Errors::InvalidShopError` for the input; if it returns, print the value and diff it against the host in the recorded WebMock request
