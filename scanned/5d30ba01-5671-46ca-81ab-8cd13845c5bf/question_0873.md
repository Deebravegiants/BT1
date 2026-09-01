# Q873: send_to_logger — attacker text into logs via response-derived messages

## Question
Trace `Logger.send_to_logger` from the private `send_to_logger`, which prefixes every message with `context(log_level)` and forwards to `Context.logger` with deprecation reasons and error messages built from upstream response content in `HttpClient#request`: because strings taken from a response are logged verbatim, so an upstream-influenced value shapes log content, does the value that was verified stop being the value that is used? Prove the break against CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted and map it to Critical - cross-tenant access: one shop's request reads or mutates another merchant's data.

## Target
- File/function: `lib/shopify_api/logger.rb` -> `Logger.send_to_logger`
- Entrypoint: the private `send_to_logger`, which prefixes every message with `context(log_level)` and forwards to `Context.logger`
- Attacker controls: deprecation reasons and error messages built from upstream response content in `HttpClient#request`
- Exploit idea: strings taken from a response are logged verbatim, so an upstream-influenced value shapes log content
- Invariant to test: CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted
- Expected Immunefi impact: Critical - cross-tenant access: one shop's request reads or mutates another merchant's data (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest: stub a response with a deprecation header containing newlines and assert the emitted log line count is unchanged
