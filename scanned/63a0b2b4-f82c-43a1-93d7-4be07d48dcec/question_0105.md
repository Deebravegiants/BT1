# Q105: uri_from_shop_domain — shop name reconstructed, not validated via IDN / Unicode label

## Question
Can an unprivileged attacker reach `ShopValidator.uri_from_shop_domain` through the private `uri_from_shop_domain` normalisation step that downcases, strips, rejects `@` and prepends `https://` before `Addressable::URI.parse` while supplying a shop string using non-ASCII or Unicode-normalising labels (fullwidth dot, Cyrillic homoglyph, soft hyphen) that survive `downcase.strip`, so that the returned `"#{shop}.myshopify.com"` is manufactured by string concatenation and never re-validated, breaking the requirement that SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host, and ending in Critical - exfiltration of the app's `client_secret` and/or the OAuth authorization `code`?

## Target
- File/function: `lib/shopify_api/utils/shop_validator.rb` -> `ShopValidator.uri_from_shop_domain`
- Entrypoint: the private `uri_from_shop_domain` normalisation step that downcases, strips, rejects `@` and prepends `https://` before `Addressable::URI.parse`
- Attacker controls: a shop string using non-ASCII or Unicode-normalising labels (fullwidth dot, Cyrillic homoglyph, soft hyphen) that survive `downcase.strip`
- Exploit idea: the returned `"#{shop}.myshopify.com"` is manufactured by string concatenation and never re-validated
- Invariant to test: SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host
- Expected Immunefi impact: Critical - exfiltration of the app's `client_secret` and/or the OAuth authorization `code` (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: table-driven minitest asserting `sanitize_shop_domain` returns `nil` for the candidate string, then assert the same string through `URI`/HTTParty resolves elsewhere
