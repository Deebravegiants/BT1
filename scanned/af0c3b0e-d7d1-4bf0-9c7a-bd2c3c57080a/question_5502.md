# Q5502: sanitize! — differential between the two entry points via empty path segment

## Question
Can an unprivileged attacker reach `ShopValidator.sanitize!` through `ShopValidator.sanitize!`, reached from `ClientCredentials.client_credentials`, `RefreshToken.refresh_access_token` and `TokenExchange.migrate_to_expiring_token` with a caller-supplied `shop` while supplying a unified-admin URL whose path ends in a slash or is empty, so `path.split('/').last` yields `nil` or the literal store name of another merchant, so that `sanitize_shop_domain` returns `nil` where `sanitize!` raises, or vice versa, so callers that only check for `nil` behave differently from callers that rescue, breaking the requirement that SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source, and ending in High - SSRF: an authenticated request carrying the app's credentials is driven to an unintended host?

## Target
- File/function: `lib/shopify_api/utils/shop_validator.rb` -> `ShopValidator.sanitize!`
- Entrypoint: `ShopValidator.sanitize!`, reached from `ClientCredentials.client_credentials`, `RefreshToken.refresh_access_token` and `TokenExchange.migrate_to_expiring_token` with a caller-supplied `shop`
- Attacker controls: a unified-admin URL whose path ends in a slash or is empty, so `path.split('/').last` yields `nil` or the literal store name of another merchant
- Exploit idea: `sanitize_shop_domain` returns `nil` where `sanitize!` raises, or vice versa, so callers that only check for `nil` behave differently from callers that rescue
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: High - SSRF: an authenticated request carrying the app's credentials is driven to an unintended host (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `sanitize!` raises `Errors::InvalidShopError` for the input; if it returns, print the value and diff it against the host in the recorded WebMock request
