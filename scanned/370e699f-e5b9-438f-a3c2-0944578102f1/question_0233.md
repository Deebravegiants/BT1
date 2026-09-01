# Q233: send_to_logger — no sanitisation via shop in the prefix

## Question
Does `Logger.send_to_logger` collapse two distinct identities into one when an unprivileged attacker submits the active session's shop, embedded in every line, which reveals which tenant a worker is serving at the private `send_to_logger`, which prefixes every message with `context(log_level)` and forwards to `Context.logger`? Show that no redaction pass exists for tokens, secrets or newlines before writing, that CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted is violated, and that the consequence is Critical - cross-tenant access: one shop's request reads or mutates another merchant's data.

## Target
- File/function: `lib/shopify_api/logger.rb` -> `Logger.send_to_logger`
- Entrypoint: the private `send_to_logger`, which prefixes every message with `context(log_level)` and forwards to `Context.logger`
- Attacker controls: the active session's shop, embedded in every line, which reveals which tenant a worker is serving
- Exploit idea: no redaction pass exists for tokens, secrets or newlines before writing
- Invariant to test: CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted
- Expected Immunefi impact: Critical - cross-tenant access: one shop's request reads or mutates another merchant's data (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert the shop prefix matches the shop of the request being served, not a stale thread-local
