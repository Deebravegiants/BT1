# Q1601: sanitize! — trusted list widened per call via empty path segment

## Question
Trace `ShopValidator.sanitize!` from `ShopValidator.sanitize!`, reached from `ClientCredentials.client_credentials`, `RefreshToken.refresh_access_token` and `TokenExchange.migrate_to_expiring_token` with a caller-supplied `shop` with a unified-admin URL whose path ends in a slash or is empty, so `path.split('/').last` yields `nil` or the literal store name of another merchant: because `trusted_domains` mutates a dup of the constant with a caller-supplied value, so the trust set is request-scoped, does the value that was verified stop being the value that is used? Prove the break against SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host and map it to Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`).

## Target
- File/function: `lib/shopify_api/utils/shop_validator.rb` -> `ShopValidator.sanitize!`
- Entrypoint: `ShopValidator.sanitize!`, reached from `ClientCredentials.client_credentials`, `RefreshToken.refresh_access_token` and `TokenExchange.migrate_to_expiring_token` with a caller-supplied `shop`
- Attacker controls: a unified-admin URL whose path ends in a slash or is empty, so `path.split('/').last` yields `nil` or the literal store name of another merchant
- Exploit idea: `trusted_domains` mutates a dup of the constant with a caller-supplied value, so the trust set is request-scoped
- Invariant to test: SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host
- Expected Immunefi impact: Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`) (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: table-driven minitest asserting `sanitize_shop_domain` returns `nil` for the candidate string, then assert the same string through `URI`/HTTParty resolves elsewhere
