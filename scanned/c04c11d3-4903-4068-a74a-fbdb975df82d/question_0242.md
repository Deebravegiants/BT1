# Q242: migrate_to_expiring_token — client_secret sent to a derived host via deprecated shop argument

## Question
Can the still-accepted `shop:` keyword, which is now ignored in favour of `dest` but may be what the host app validated, supplied by an unprivileged attacker at `migrate_to_expiring_token(shop:, non_expiring_offline_token:)`, make `TokenExchange.migrate_to_expiring_token` and the code consuming its result disagree, given that the POST body carries `client_id` and `client_secret` to `https://#{dest_shop}/admin/oauth/access_token`? The binding to test is SESSION DERIVATION: a session id is derived only from bytes authenticated under `Context.api_secret_key`; the impact to prove is Critical - cross-tenant access: one shop's request reads or mutates another merchant's data.

## Target
- File/function: `lib/shopify_api/auth/token_exchange.rb` -> `TokenExchange.migrate_to_expiring_token`
- Entrypoint: `migrate_to_expiring_token(shop:, non_expiring_offline_token:)`
- Attacker controls: the still-accepted `shop:` keyword, which is now ignored in favour of `dest` but may be what the host app validated
- Exploit idea: the POST body carries `client_id` and `client_secret` to `https://#{dest_shop}/admin/oauth/access_token`
- Invariant to test: SESSION DERIVATION: a session id is derived only from bytes authenticated under `Context.api_secret_key`
- Expected Immunefi impact: Critical - cross-tenant access: one shop's request reads or mutates another merchant's data (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: pass a validated `shop:` that differs from `dest` and assert the code raises rather than silently preferring `dest`
