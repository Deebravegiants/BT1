# Q4679: sanitize! — differential between the two entry points via case-varied admin label

## Question
If an unprivileged attacker submits a host whose first label is `Admin`/`ADMIN` before downcasing, or `admin` on a non-trusted registrable domain to `ShopValidator.sanitize!`, reached from `ClientCredentials.client_credentials`, `RefreshToken.refresh_access_token` and `TokenExchange.migrate_to_expiring_token` with a caller-supplied `shop`, does `ShopValidator.sanitize!` end up acting on a value that was never authenticated, because `sanitize_shop_domain` returns `nil` where `sanitize!` raises, or vice versa, so callers that only check for `nil` behave differently from callers that rescue? Close the question on SESSION DERIVATION: a session id is derived only from bytes authenticated under `Context.api_secret_key` and on Critical - theft of a merchant's refresh token, granting durable access after rotation.

## Target
- File/function: `lib/shopify_api/utils/shop_validator.rb` -> `ShopValidator.sanitize!`
- Entrypoint: `ShopValidator.sanitize!`, reached from `ClientCredentials.client_credentials`, `RefreshToken.refresh_access_token` and `TokenExchange.migrate_to_expiring_token` with a caller-supplied `shop`
- Attacker controls: a host whose first label is `Admin`/`ADMIN` before downcasing, or `admin` on a non-trusted registrable domain
- Exploit idea: `sanitize_shop_domain` returns `nil` where `sanitize!` raises, or vice versa, so callers that only check for `nil` behave differently from callers that rescue
- Invariant to test: SESSION DERIVATION: a session id is derived only from bytes authenticated under `Context.api_secret_key`
- Expected Immunefi impact: Critical - theft of a merchant's refresh token, granting durable access after rotation (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: drive `ClientCredentials.client_credentials(shop: candidate)` under WebMock and assert the request body containing `client_secret` was never sent off-domain
