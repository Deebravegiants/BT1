# Q5470: sanitize_shop_domain — trusted list widened per call via percent-encoded separator

## Question
If an unprivileged attacker submits a shop string with percent-encoded path/host separators such as `admin.shopify.com%2Fstore%2Fvictim` or `%2e%2e` segments to a host-app route that forwards a user-supplied `shop` query parameter into `ShopifyAPI::Utils::ShopValidator.sanitize_shop_domain`, does `ShopValidator.sanitize_shop_domain` end up acting on a value that was never authenticated, because `trusted_domains` mutates a dup of the constant with a caller-supplied value, so the trust set is request-scoped? Close the question on SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source and on Critical - exfiltration of the app's `client_secret` and/or the OAuth authorization `code`.

## Target
- File/function: `lib/shopify_api/utils/shop_validator.rb` -> `ShopValidator.sanitize_shop_domain`
- Entrypoint: a host-app route that forwards a user-supplied `shop` query parameter into `ShopifyAPI::Utils::ShopValidator.sanitize_shop_domain`
- Attacker controls: a shop string with percent-encoded path/host separators such as `admin.shopify.com%2Fstore%2Fvictim` or `%2e%2e` segments
- Exploit idea: `trusted_domains` mutates a dup of the constant with a caller-supplied value, so the trust set is request-scoped
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: Critical - exfiltration of the app's `client_secret` and/or the OAuth authorization `code` (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `sanitize!` raises `Errors::InvalidShopError` for the input; if it returns, print the value and diff it against the host in the recorded WebMock request
