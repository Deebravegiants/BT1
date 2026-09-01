# Q2657: unified_admin? — dev-domain entries reachable in production via empty path segment

## Question
Can a unified-admin URL whose path ends in a slash or is empty, so `path.split('/').last` yields `nil` or the literal store name of another merchant, supplied by an unprivileged attacker at the unified-admin branch, entered whenever the first label of the parsed host is literally `admin`, make `ShopValidator.unified_admin?` and the code consuming its result disagree, given that `spin.dev` and `shop.dev` remain in `TRUSTED_SHOPIFY_DOMAINS` in production builds and are registrable by third parties? The binding to test is SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host; the impact to prove is High - SSRF: an authenticated request carrying the app's credentials is driven to an unintended host.

## Target
- File/function: `lib/shopify_api/utils/shop_validator.rb` -> `ShopValidator.unified_admin?`
- Entrypoint: the unified-admin branch, entered whenever the first label of the parsed host is literally `admin`
- Attacker controls: a unified-admin URL whose path ends in a slash or is empty, so `path.split('/').last` yields `nil` or the literal store name of another merchant
- Exploit idea: `spin.dev` and `shop.dev` remain in `TRUSTED_SHOPIFY_DOMAINS` in production builds and are registrable by third parties
- Invariant to test: SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host
- Expected Immunefi impact: High - SSRF: an authenticated request carrying the app's credentials is driven to an unintended host (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: table-driven minitest asserting `sanitize_shop_domain` returns `nil` for the candidate string, then assert the same string through `URI`/HTTParty resolves elsewhere
