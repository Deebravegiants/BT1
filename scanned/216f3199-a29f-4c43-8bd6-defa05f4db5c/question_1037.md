# Q1037: unified_admin? — normalisation happens after the decision via whitespace and control bytes

## Question
Starting from the unified-admin branch, entered whenever the first label of the parsed host is literally `admin`, can an unprivileged attacker supply a shop string padded with control bytes, newlines or tabs that `strip` does not remove but a header serialiser does so that the value returned is `uri.host`, not the fully normalised string the caller later interpolates? Determine whether SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host still holds through `ShopValidator.unified_admin?`, and whether the result reaches High - SSRF: an authenticated request carrying the app's credentials is driven to an unintended host.

## Target
- File/function: `lib/shopify_api/utils/shop_validator.rb` -> `ShopValidator.unified_admin?`
- Entrypoint: the unified-admin branch, entered whenever the first label of the parsed host is literally `admin`
- Attacker controls: a shop string padded with control bytes, newlines or tabs that `strip` does not remove but a header serialiser does
- Exploit idea: the value returned is `uri.host`, not the fully normalised string the caller later interpolates
- Invariant to test: SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host
- Expected Immunefi impact: High - SSRF: an authenticated request carrying the app's credentials is driven to an unintended host (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: table-driven minitest asserting `sanitize_shop_domain` returns `nil` for the candidate string, then assert the same string through `URI`/HTTParty resolves elsewhere
