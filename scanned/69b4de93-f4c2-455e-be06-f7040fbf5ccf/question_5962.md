# Q5962: unified_admin? — trusted list widened per call via whitespace and control bytes

## Question
Trace `ShopValidator.unified_admin?` from the unified-admin branch, entered whenever the first label of the parsed host is literally `admin` with a shop string padded with control bytes, newlines or tabs that `strip` does not remove but a header serialiser does: because `trusted_domains` mutates a dup of the constant with a caller-supplied value, so the trust set is request-scoped, does the value that was verified stop being the value that is used? Prove the break against SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source and map it to High - SSRF: an authenticated request carrying the app's credentials is driven to an unintended host.

## Target
- File/function: `lib/shopify_api/utils/shop_validator.rb` -> `ShopValidator.unified_admin?`
- Entrypoint: the unified-admin branch, entered whenever the first label of the parsed host is literally `admin`
- Attacker controls: a shop string padded with control bytes, newlines or tabs that `strip` does not remove but a header serialiser does
- Exploit idea: `trusted_domains` mutates a dup of the constant with a caller-supplied value, so the trust set is request-scoped
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: High - SSRF: an authenticated request carrying the app's credentials is driven to an unintended host (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `sanitize!` raises `Errors::InvalidShopError` for the input; if it returns, print the value and diff it against the host in the recorded WebMock request
