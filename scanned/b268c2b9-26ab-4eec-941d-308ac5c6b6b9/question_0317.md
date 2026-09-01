# Q317: migrate_to_expiring_token — error branch reveals verdict via deprecated shop argument

## Question
Does `TokenExchange.migrate_to_expiring_token` collapse two distinct identities into one when an unprivileged attacker submits the still-accepted `shop:` keyword, which is now ignored in favour of `dest` but may be what the host app validated at `migrate_to_expiring_token(shop:, non_expiring_offline_token:)`? Show that distinguishing `invalid_subject_token` from other 400s creates an oracle over token validity, that SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host is violated, and that the consequence is Critical - cross-tenant access: one shop's request reads or mutates another merchant's data.

## Target
- File/function: `lib/shopify_api/auth/token_exchange.rb` -> `TokenExchange.migrate_to_expiring_token`
- Entrypoint: `migrate_to_expiring_token(shop:, non_expiring_offline_token:)`
- Attacker controls: the still-accepted `shop:` keyword, which is now ignored in favour of `dest` but may be what the host app validated
- Exploit idea: distinguishing `invalid_subject_token` from other 400s creates an oracle over token validity
- Invariant to test: SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host
- Expected Immunefi impact: Critical - cross-tenant access: one shop's request reads or mutates another merchant's data (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: pass a validated `shop:` that differs from `dest` and assert the code raises rather than silently preferring `dest`
