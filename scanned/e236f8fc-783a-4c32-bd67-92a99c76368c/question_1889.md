# Q1889: unified_admin? — differential between the two entry points via trailing-dot host

## Question
Is there a reachable state in which an unprivileged attacker, controlling a shop string with a fully-qualified trailing dot such as `victim.myshopify.com.` so that the parsed `domain` and the host an HTTP client actually resolves differ at the unified-admin branch, entered whenever the first label of the parsed host is literally `admin`, makes `ShopValidator.unified_admin?` return a result the caller treats as authenticated, given that `sanitize_shop_domain` returns `nil` where `sanitize!` raises, or vice versa, so callers that only check for `nil` behave differently from callers that rescue? Test SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host and quantify Critical - theft of a merchant's refresh token, granting durable access after rotation.

## Target
- File/function: `lib/shopify_api/utils/shop_validator.rb` -> `ShopValidator.unified_admin?`
- Entrypoint: the unified-admin branch, entered whenever the first label of the parsed host is literally `admin`
- Attacker controls: a shop string with a fully-qualified trailing dot such as `victim.myshopify.com.` so that the parsed `domain` and the host an HTTP client actually resolves differ
- Exploit idea: `sanitize_shop_domain` returns `nil` where `sanitize!` raises, or vice versa, so callers that only check for `nil` behave differently from callers that rescue
- Invariant to test: SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host
- Expected Immunefi impact: Critical - theft of a merchant's refresh token, granting durable access after rotation (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: table-driven minitest asserting `sanitize_shop_domain` returns `nil` for the candidate string, then assert the same string through `URI`/HTTParty resolves elsewhere
