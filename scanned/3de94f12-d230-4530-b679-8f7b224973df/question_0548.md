# Q548: context — debug paths carry credentials via error message content

## Question
Does `Logger.context` collapse two distinct identities into one when an unprivileged attacker submits the `serialized_error` JSON, which is built from response body and headers at `context`, which embeds `ShopifyAPI::Context.active_session&.shop` in every log line? Show that debug logging around token flows can include request or error detail derived from bodies that carried `client_secret`, that SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source is violated, and that the consequence is High - credential or token leakage into log output or error messages.

## Target
- File/function: `lib/shopify_api/logger.rb` -> `Logger.context`
- Entrypoint: `context`, which embeds `ShopifyAPI::Context.active_session&.shop` in every log line
- Attacker controls: the `serialized_error` JSON, which is built from response body and headers
- Exploit idea: debug logging around token flows can include request or error detail derived from bodies that carried `client_secret`
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: High - credential or token leakage into log output or error messages (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert the shop prefix matches the shop of the request being served, not a stale thread-local
