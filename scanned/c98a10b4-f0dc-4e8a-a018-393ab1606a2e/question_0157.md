# Q157: uri_from_shop_domain — trusted list widened per call via suffix-confusion host

## Question
If an unprivileged attacker submits a host whose registrable domain matches a trusted entry only under `Addressable`'s public-suffix view, e.g. `myshopify.com.evil.example` or `evil-myshopify.com` to the private `uri_from_shop_domain` normalisation step that downcases, strips, rejects `@` and prepends `https://` before `Addressable::URI.parse`, does `ShopValidator.uri_from_shop_domain` end up acting on a value that was never authenticated, because `trusted_domains` mutates a dup of the constant with a caller-supplied value, so the trust set is request-scoped? Close the question on SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host and on High - SSRF: an authenticated request carrying the app's credentials is driven to an unintended host.

## Target
- File/function: `lib/shopify_api/utils/shop_validator.rb` -> `ShopValidator.uri_from_shop_domain`
- Entrypoint: the private `uri_from_shop_domain` normalisation step that downcases, strips, rejects `@` and prepends `https://` before `Addressable::URI.parse`
- Attacker controls: a host whose registrable domain matches a trusted entry only under `Addressable`'s public-suffix view, e.g. `myshopify.com.evil.example` or `evil-myshopify.com`
- Exploit idea: `trusted_domains` mutates a dup of the constant with a caller-supplied value, so the trust set is request-scoped
- Invariant to test: SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host
- Expected Immunefi impact: High - SSRF: an authenticated request carrying the app's credentials is driven to an unintended host (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: table-driven minitest asserting `sanitize_shop_domain` returns `nil` for the candidate string, then assert the same string through `URI`/HTTParty resolves elsewhere
