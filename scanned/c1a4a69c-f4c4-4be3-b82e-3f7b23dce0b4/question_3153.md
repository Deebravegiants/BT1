# Q3153: uri_from_shop_domain — normalisation happens after the decision via trailing-dot host

## Question
If an unprivileged attacker submits a shop string with a fully-qualified trailing dot such as `victim.myshopify.com.` so that the parsed `domain` and the host an HTTP client actually resolves differ to the private `uri_from_shop_domain` normalisation step that downcases, strips, rejects `@` and prepends `https://` before `Addressable::URI.parse`, does `ShopValidator.uri_from_shop_domain` end up acting on a value that was never authenticated, because the value returned is `uri.host`, not the fully normalised string the caller later interpolates? Close the question on SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host and on Critical - cross-tenant access: one shop's request reads or mutates another merchant's data.

## Target
- File/function: `lib/shopify_api/utils/shop_validator.rb` -> `ShopValidator.uri_from_shop_domain`
- Entrypoint: the private `uri_from_shop_domain` normalisation step that downcases, strips, rejects `@` and prepends `https://` before `Addressable::URI.parse`
- Attacker controls: a shop string with a fully-qualified trailing dot such as `victim.myshopify.com.` so that the parsed `domain` and the host an HTTP client actually resolves differ
- Exploit idea: the value returned is `uri.host`, not the fully normalised string the caller later interpolates
- Invariant to test: SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host
- Expected Immunefi impact: Critical - cross-tenant access: one shop's request reads or mutates another merchant's data (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: table-driven minitest asserting `sanitize_shop_domain` returns `nil` for the candidate string, then assert the same string through `URI`/HTTParty resolves elsewhere
