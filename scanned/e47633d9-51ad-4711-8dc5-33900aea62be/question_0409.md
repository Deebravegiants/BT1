# Q409: unified_admin? — normalisation happens after the decision via userinfo bypass

## Question
If an unprivileged attacker submits a shop string that expresses userinfo without a literal `@` (encoded `%40`) so the `name.include?("@")` guard is skipped to the unified-admin branch, entered whenever the first label of the parsed host is literally `admin`, does `ShopValidator.unified_admin?` end up acting on a value that was never authenticated, because the value returned is `uri.host`, not the fully normalised string the caller later interpolates? Close the question on SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host and on Critical - theft of a merchant's refresh token, granting durable access after rotation.

## Target
- File/function: `lib/shopify_api/utils/shop_validator.rb` -> `ShopValidator.unified_admin?`
- Entrypoint: the unified-admin branch, entered whenever the first label of the parsed host is literally `admin`
- Attacker controls: a shop string that expresses userinfo without a literal `@` (encoded `%40`) so the `name.include?("@")` guard is skipped
- Exploit idea: the value returned is `uri.host`, not the fully normalised string the caller later interpolates
- Invariant to test: SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host
- Expected Immunefi impact: Critical - theft of a merchant's refresh token, granting durable access after rotation (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: table-driven minitest asserting `sanitize_shop_domain` returns `nil` for the candidate string, then assert the same string through `URI`/HTTParty resolves elsewhere
