# Q53: uri_from_shop_domain — shop name reconstructed, not validated via empty path segment

## Question
Can a unified-admin URL whose path ends in a slash or is empty, so `path.split('/').last` yields `nil` or the literal store name of another merchant, supplied by an unprivileged attacker at the private `uri_from_shop_domain` normalisation step that downcases, strips, rejects `@` and prepends `https://` before `Addressable::URI.parse`, make `ShopValidator.uri_from_shop_domain` and the code consuming its result disagree, given that the returned `"#{shop}.myshopify.com"` is manufactured by string concatenation and never re-validated? The binding to test is SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host; the impact to prove is Critical - cross-tenant access: one shop's request reads or mutates another merchant's data.

## Target
- File/function: `lib/shopify_api/utils/shop_validator.rb` -> `ShopValidator.uri_from_shop_domain`
- Entrypoint: the private `uri_from_shop_domain` normalisation step that downcases, strips, rejects `@` and prepends `https://` before `Addressable::URI.parse`
- Attacker controls: a unified-admin URL whose path ends in a slash or is empty, so `path.split('/').last` yields `nil` or the literal store name of another merchant
- Exploit idea: the returned `"#{shop}.myshopify.com"` is manufactured by string concatenation and never re-validated
- Invariant to test: SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host
- Expected Immunefi impact: Critical - cross-tenant access: one shop's request reads or mutates another merchant's data (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: table-driven minitest asserting `sanitize_shop_domain` returns `nil` for the candidate string, then assert the same string through `URI`/HTTParty resolves elsewhere
