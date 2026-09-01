# Q578: migrate_to_expiring_token — error branch reveals verdict via error-path body

## Question
Can a 400 response whose `error` field steers the `invalid_subject_token` branch, supplied by an unprivileged attacker at `migrate_to_expiring_token(shop:, non_expiring_offline_token:)`, make `TokenExchange.migrate_to_expiring_token` and the code consuming its result disagree, given that distinguishing `invalid_subject_token` from other 400s creates an oracle over token validity? The binding to test is SESSION DERIVATION: a session id is derived only from bytes authenticated under `Context.api_secret_key`; the impact to prove is Critical - theft of a merchant's refresh token, granting durable access after rotation.

## Target
- File/function: `lib/shopify_api/auth/token_exchange.rb` -> `TokenExchange.migrate_to_expiring_token`
- Entrypoint: `migrate_to_expiring_token(shop:, non_expiring_offline_token:)`
- Attacker controls: a 400 response whose `error` field steers the `invalid_subject_token` branch
- Exploit idea: distinguishing `invalid_subject_token` from other 400s creates an oracle over token validity
- Invariant to test: SESSION DERIVATION: a session id is derived only from bytes authenticated under `Context.api_secret_key`
- Expected Immunefi impact: Critical - theft of a merchant's refresh token, granting durable access after rotation (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: pass a validated `shop:` that differs from `dest` and assert the code raises rather than silently preferring `dest`
