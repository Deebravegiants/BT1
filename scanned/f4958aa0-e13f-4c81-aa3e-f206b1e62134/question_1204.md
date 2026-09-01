# Q1204: context — attacker text into logs via error message content

## Question
Can an unprivileged attacker reach `Logger.context` through `context`, which embeds `ShopifyAPI::Context.active_session&.shop` in every log line while supplying the `serialized_error` JSON, which is built from response body and headers, so that strings taken from a response are logged verbatim, so an upstream-influenced value shapes log content, breaking the requirement that SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source, and ending in High - credential or token leakage into log output or error messages?

## Target
- File/function: `lib/shopify_api/logger.rb` -> `Logger.context`
- Entrypoint: `context`, which embeds `ShopifyAPI::Context.active_session&.shop` in every log line
- Attacker controls: the `serialized_error` JSON, which is built from response body and headers
- Exploit idea: strings taken from a response are logged verbatim, so an upstream-influenced value shapes log content
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: High - credential or token leakage into log output or error messages (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert no code path logs `access_token`, `refresh_token` or `client_secret`, by asserting on a captured logger
