# Q367: migrate_to_expiring_token — no consumption tracking via expiring flag

## Question
If an unprivileged attacker submits `Context.expiring_offline_access_tokens`, which changes the body sent and the session's expiry to `migrate_to_expiring_token(shop:, non_expiring_offline_token:)`, does `TokenExchange.migrate_to_expiring_token` end up acting on a value that was never authenticated, because a subject token can be exchanged repeatedly within its validity window? Close the question on SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source and on Critical - cross-tenant access: one shop's request reads or mutates another merchant's data.

## Target
- File/function: `lib/shopify_api/auth/token_exchange.rb` -> `TokenExchange.migrate_to_expiring_token`
- Entrypoint: `migrate_to_expiring_token(shop:, non_expiring_offline_token:)`
- Attacker controls: `Context.expiring_offline_access_tokens`, which changes the body sent and the session's expiry
- Exploit idea: a subject token can be exchanged repeatedly within its validity window
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: Critical - cross-tenant access: one shop's request reads or mutates another merchant's data (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `exchange_token` sanitises `dest_shop` the same way `migrate_to_expiring_token` sanitises its `shop:` argument
