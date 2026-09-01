# Q284: send_to_logger — tenant identity in every line via shop in the prefix

## Question
Can the active session's shop, embedded in every line, which reveals which tenant a worker is serving, supplied by an unprivileged attacker at the private `send_to_logger`, which prefixes every message with `context(log_level)` and forwards to `Context.logger`, make `Logger.send_to_logger` and the code consuming its result disagree, given that the shop prefix is derived from thread-local state that may be stale? The binding to test is SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source; the impact to prove is High - credential or token leakage into log output or error messages.

## Target
- File/function: `lib/shopify_api/logger.rb` -> `Logger.send_to_logger`
- Entrypoint: the private `send_to_logger`, which prefixes every message with `context(log_level)` and forwards to `Context.logger`
- Attacker controls: the active session's shop, embedded in every line, which reveals which tenant a worker is serving
- Exploit idea: the shop prefix is derived from thread-local state that may be stale
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: High - credential or token leakage into log output or error messages (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert the shop prefix matches the shop of the request being served, not a stale thread-local
