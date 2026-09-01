# Q1057: sanitize! — trusted list widened per call via backslash separator

## Question
Can an unprivileged attacker reach `ShopValidator.sanitize!` through `ShopValidator.sanitize!`, reached from `ClientCredentials.client_credentials`, `RefreshToken.refresh_access_token` and `TokenExchange.migrate_to_expiring_token` with a caller-supplied `shop` while supplying a shop string using a backslash instead of a slash (`https:\\evil.example\admin`), which `Addressable` and HTTParty disagree about, so that `trusted_domains` mutates a dup of the constant with a caller-supplied value, so the trust set is request-scoped, breaking the requirement that SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host, and ending in High - SSRF: an authenticated request carrying the app's credentials is driven to an unintended host?

## Target
- File/function: `lib/shopify_api/utils/shop_validator.rb` -> `ShopValidator.sanitize!`
- Entrypoint: `ShopValidator.sanitize!`, reached from `ClientCredentials.client_credentials`, `RefreshToken.refresh_access_token` and `TokenExchange.migrate_to_expiring_token` with a caller-supplied `shop`
- Attacker controls: a shop string using a backslash instead of a slash (`https:\\evil.example\admin`), which `Addressable` and HTTParty disagree about
- Exploit idea: `trusted_domains` mutates a dup of the constant with a caller-supplied value, so the trust set is request-scoped
- Invariant to test: SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host
- Expected Immunefi impact: High - SSRF: an authenticated request carrying the app's credentials is driven to an unintended host (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: table-driven minitest asserting `sanitize_shop_domain` returns `nil` for the candidate string, then assert the same string through `URI`/HTTParty resolves elsewhere
