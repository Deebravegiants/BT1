# Q1096: context — tenant identity in every line via newline injection

## Question
Can response-controlled strings containing newlines, which forge additional log lines, supplied by an unprivileged attacker at `context`, which embeds `ShopifyAPI::Context.active_session&.shop` in every log line, make `Logger.context` and the code consuming its result disagree, given that the shop prefix is derived from thread-local state that may be stale? The binding to test is SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source; the impact to prove is High - credential or token leakage into log output or error messages.

## Target
- File/function: `lib/shopify_api/logger.rb` -> `Logger.context`
- Entrypoint: `context`, which embeds `ShopifyAPI::Context.active_session&.shop` in every log line
- Attacker controls: response-controlled strings containing newlines, which forge additional log lines
- Exploit idea: the shop prefix is derived from thread-local state that may be stale
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: High - credential or token leakage into log output or error messages (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert no code path logs `access_token`, `refresh_token` or `client_secret`, by asserting on a captured logger
