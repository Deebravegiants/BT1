# Q3043: sanitize! — shop name reconstructed, not validated via dotless name

## Question
Trace `ShopValidator.sanitize!` from `ShopValidator.sanitize!`, reached from `ClientCredentials.client_credentials`, `RefreshToken.refresh_access_token` and `TokenExchange.migrate_to_expiring_token` with a caller-supplied `shop` with a dotless shop name that takes the `name += ".#{myshopify_domain}"` branch only when `myshopify_domain` is present, yielding a different verdict for the same input: because the returned `"#{shop}.myshopify.com"` is manufactured by string concatenation and never re-validated, does the value that was verified stop being the value that is used? Prove the break against SESSION DERIVATION: a session id is derived only from bytes authenticated under `Context.api_secret_key` and map it to Critical - cross-tenant access: one shop's request reads or mutates another merchant's data.

## Target
- File/function: `lib/shopify_api/utils/shop_validator.rb` -> `ShopValidator.sanitize!`
- Entrypoint: `ShopValidator.sanitize!`, reached from `ClientCredentials.client_credentials`, `RefreshToken.refresh_access_token` and `TokenExchange.migrate_to_expiring_token` with a caller-supplied `shop`
- Attacker controls: a dotless shop name that takes the `name += ".#{myshopify_domain}"` branch only when `myshopify_domain` is present, yielding a different verdict for the same input
- Exploit idea: the returned `"#{shop}.myshopify.com"` is manufactured by string concatenation and never re-validated
- Invariant to test: SESSION DERIVATION: a session id is derived only from bytes authenticated under `Context.api_secret_key`
- Expected Immunefi impact: Critical - cross-tenant access: one shop's request reads or mutates another merchant's data (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: drive `ClientCredentials.client_credentials(shop: candidate)` under WebMock and assert the request body containing `client_secret` was never sent off-domain
