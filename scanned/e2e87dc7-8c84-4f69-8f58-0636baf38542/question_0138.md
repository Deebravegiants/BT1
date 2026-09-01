# Q138: migrate_to_expiring_token — session keyed by claim via expiring flag

## Question
Trace `TokenExchange.migrate_to_expiring_token` from `migrate_to_expiring_token(shop:, non_expiring_offline_token:)` with `Context.expiring_offline_access_tokens`, which changes the body sent and the session's expiry: because `Session.from(shop: dest_shop, ...)` mints the storage key from the same unvalidated claim, does the value that was verified stop being the value that is used? Prove the break against SESSION DERIVATION: a session id is derived only from bytes authenticated under `Context.api_secret_key` and map it to Critical - theft of a merchant's refresh token, granting durable access after rotation.

## Target
- File/function: `lib/shopify_api/auth/token_exchange.rb` -> `TokenExchange.migrate_to_expiring_token`
- Entrypoint: `migrate_to_expiring_token(shop:, non_expiring_offline_token:)`
- Attacker controls: `Context.expiring_offline_access_tokens`, which changes the body sent and the session's expiry
- Exploit idea: `Session.from(shop: dest_shop, ...)` mints the storage key from the same unvalidated claim
- Invariant to test: SESSION DERIVATION: a session id is derived only from bytes authenticated under `Context.api_secret_key`
- Expected Immunefi impact: Critical - theft of a merchant's refresh token, granting durable access after rotation (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest + WebMock: mint a token whose `dest` is a non-Shopify host, call `exchange_token`, and assert no request carrying `client_secret` left for that host
