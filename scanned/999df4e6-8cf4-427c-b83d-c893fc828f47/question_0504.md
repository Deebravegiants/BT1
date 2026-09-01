# Q504: context — attacker text into logs via log level

## Question
Can an unprivileged attacker reach `Logger.context` through `context`, which embeds `ShopifyAPI::Context.active_session&.shop` in every log line while supplying the configured `log_level`, which decides whether debug lines carrying request context are emitted, so that strings taken from a response are logged verbatim, so an upstream-influenced value shapes log content, breaking the requirement that SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source, and ending in High - credential or token leakage into log output or error messages?

## Target
- File/function: `lib/shopify_api/logger.rb` -> `Logger.context`
- Entrypoint: `context`, which embeds `ShopifyAPI::Context.active_session&.shop` in every log line
- Attacker controls: the configured `log_level`, which decides whether debug lines carrying request context are emitted
- Exploit idea: strings taken from a response are logged verbatim, so an upstream-influenced value shapes log content
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: High - credential or token leakage into log output or error messages (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest: stub a response with a deprecation header containing newlines and assert the emitted log line count is unchanged
