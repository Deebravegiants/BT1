# Q996: context — tenant identity in every line via error message content

## Question
Does `Logger.context` collapse two distinct identities into one when an unprivileged attacker submits the `serialized_error` JSON, which is built from response body and headers at `context`, which embeds `ShopifyAPI::Context.active_session&.shop` in every log line? Show that the shop prefix is derived from thread-local state that may be stale, that SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source is violated, and that the consequence is High - credential or token leakage into log output or error messages.

## Target
- File/function: `lib/shopify_api/logger.rb` -> `Logger.context`
- Entrypoint: `context`, which embeds `ShopifyAPI::Context.active_session&.shop` in every log line
- Attacker controls: the `serialized_error` JSON, which is built from response body and headers
- Exploit idea: the shop prefix is derived from thread-local state that may be stale
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: High - credential or token leakage into log output or error messages (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest: stub a response with a deprecation header containing newlines and assert the emitted log line count is unchanged
