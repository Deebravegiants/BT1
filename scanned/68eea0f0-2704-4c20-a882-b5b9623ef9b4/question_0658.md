# Q658: context — no sanitisation via newline injection

## Question
Can an unprivileged attacker reach `Logger.context` through `context`, which embeds `ShopifyAPI::Context.active_session&.shop` in every log line while supplying response-controlled strings containing newlines, which forge additional log lines, so that no redaction pass exists for tokens, secrets or newlines before writing, breaking the requirement that SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source, and ending in High - credential or token leakage into log output or error messages?

## Target
- File/function: `lib/shopify_api/logger.rb` -> `Logger.context`
- Entrypoint: `context`, which embeds `ShopifyAPI::Context.active_session&.shop` in every log line
- Attacker controls: response-controlled strings containing newlines, which forge additional log lines
- Exploit idea: no redaction pass exists for tokens, secrets or newlines before writing
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: High - credential or token leakage into log output or error messages (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert no code path logs `access_token`, `refresh_token` or `client_secret`, by asserting on a captured logger
