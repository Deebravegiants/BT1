# Q384: context — tenant identity in every line via shop in the prefix

## Question
Is there a reachable state in which an unprivileged attacker, controlling the active session's shop, embedded in every line, which reveals which tenant a worker is serving at `context`, which embeds `ShopifyAPI::Context.active_session&.shop` in every log line, makes `Logger.context` return a result the caller treats as authenticated, given that the shop prefix is derived from thread-local state that may be stale? Test SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source and quantify High - credential or token leakage into log output or error messages.

## Target
- File/function: `lib/shopify_api/logger.rb` -> `Logger.context`
- Entrypoint: `context`, which embeds `ShopifyAPI::Context.active_session&.shop` in every log line
- Attacker controls: the active session's shop, embedded in every line, which reveals which tenant a worker is serving
- Exploit idea: the shop prefix is derived from thread-local state that may be stale
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: High - credential or token leakage into log output or error messages (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest: stub a response with a deprecation header containing newlines and assert the emitted log line count is unchanged
