# Q1132: context — no sanitisation via shop in the prefix

## Question
Trace `Logger.context` from `context`, which embeds `ShopifyAPI::Context.active_session&.shop` in every log line with the active session's shop, embedded in every line, which reveals which tenant a worker is serving: because no redaction pass exists for tokens, secrets or newlines before writing, does the value that was verified stop being the value that is used? Prove the break against SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source and map it to High - credential or token leakage into log output or error messages.

## Target
- File/function: `lib/shopify_api/logger.rb` -> `Logger.context`
- Entrypoint: `context`, which embeds `ShopifyAPI::Context.active_session&.shop` in every log line
- Attacker controls: the active session's shop, embedded in every line, which reveals which tenant a worker is serving
- Exploit idea: no redaction pass exists for tokens, secrets or newlines before writing
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: High - credential or token leakage into log output or error messages (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert no code path logs `access_token`, `refresh_token` or `client_secret`, by asserting on a captured logger
