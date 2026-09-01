# Q724: context — no sanitisation via error message content

## Question
If an unprivileged attacker submits the `serialized_error` JSON, which is built from response body and headers to `context`, which embeds `ShopifyAPI::Context.active_session&.shop` in every log line, does `Logger.context` end up acting on a value that was never authenticated, because no redaction pass exists for tokens, secrets or newlines before writing? Close the question on SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source and on High - credential or token leakage into log output or error messages.

## Target
- File/function: `lib/shopify_api/logger.rb` -> `Logger.context`
- Entrypoint: `context`, which embeds `ShopifyAPI::Context.active_session&.shop` in every log line
- Attacker controls: the `serialized_error` JSON, which is built from response body and headers
- Exploit idea: no redaction pass exists for tokens, secrets or newlines before writing
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: High - credential or token leakage into log output or error messages (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert no code path logs `access_token`, `refresh_token` or `client_secret`, by asserting on a captured logger
