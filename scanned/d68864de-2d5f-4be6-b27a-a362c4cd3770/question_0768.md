# Q768: deprecated — debug paths carry credentials via newline injection

## Question
Trace `Logger.deprecated` from `deprecated(message, version)`, which raises `FeatureDeprecatedError` when the version has passed with response-controlled strings containing newlines, which forge additional log lines: because debug logging around token flows can include request or error detail derived from bodies that carried `client_secret`, does the value that was verified stop being the value that is used? Prove the break against SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source and map it to High - credential or token leakage into log output or error messages.

## Target
- File/function: `lib/shopify_api/logger.rb` -> `Logger.deprecated`
- Entrypoint: `deprecated(message, version)`, which raises `FeatureDeprecatedError` when the version has passed
- Attacker controls: response-controlled strings containing newlines, which forge additional log lines
- Exploit idea: debug logging around token flows can include request or error detail derived from bodies that carried `client_secret`
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: High - credential or token leakage into log output or error messages (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest: stub a response with a deprecation header containing newlines and assert the emitted log line count is unchanged
