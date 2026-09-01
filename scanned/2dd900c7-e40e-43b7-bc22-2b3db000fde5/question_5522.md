# Q5522: myshopify_domain_from_unified_admin — shop name reconstructed, not validated via empty path segment

## Question
Is there a reachable state in which an unprivileged attacker, controlling a unified-admin URL whose path ends in a slash or is empty, so `path.split('/').last` yields `nil` or the literal store name of another merchant at `myshopify_domain_from_unified_admin`, which returns `"#{uri.path.split('/').last}.myshopify.com"` from an unvalidated path segment, makes `ShopValidator.myshopify_domain_from_unified_admin` return a result the caller treats as authenticated, given that the returned `"#{shop}.myshopify.com"` is manufactured by string concatenation and never re-validated? Test SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source and quantify High - SSRF: an authenticated request carrying the app's credentials is driven to an unintended host.

## Target
- File/function: `lib/shopify_api/utils/shop_validator.rb` -> `ShopValidator.myshopify_domain_from_unified_admin`
- Entrypoint: `myshopify_domain_from_unified_admin`, which returns `"#{uri.path.split('/').last}.myshopify.com"` from an unvalidated path segment
- Attacker controls: a unified-admin URL whose path ends in a slash or is empty, so `path.split('/').last` yields `nil` or the literal store name of another merchant
- Exploit idea: the returned `"#{shop}.myshopify.com"` is manufactured by string concatenation and never re-validated
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: High - SSRF: an authenticated request carrying the app's credentials is driven to an unintended host (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `sanitize!` raises `Errors::InvalidShopError` for the input; if it returns, print the value and diff it against the host in the recorded WebMock request
