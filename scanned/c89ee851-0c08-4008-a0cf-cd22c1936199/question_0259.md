# Q259: deprecated — tenant identity in every line via newline injection

## Question
Can an unprivileged attacker reach `Logger.deprecated` through `deprecated(message, version)`, which raises `FeatureDeprecatedError` when the version has passed while supplying response-controlled strings containing newlines, which forge additional log lines, so that the shop prefix is derived from thread-local state that may be stale, breaking the requirement that CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted, and ending in Critical - cross-tenant access: one shop's request reads or mutates another merchant's data?

## Target
- File/function: `lib/shopify_api/logger.rb` -> `Logger.deprecated`
- Entrypoint: `deprecated(message, version)`, which raises `FeatureDeprecatedError` when the version has passed
- Attacker controls: response-controlled strings containing newlines, which forge additional log lines
- Exploit idea: the shop prefix is derived from thread-local state that may be stale
- Invariant to test: CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted
- Expected Immunefi impact: Critical - cross-tenant access: one shop's request reads or mutates another merchant's data (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert no code path logs `access_token`, `refresh_token` or `client_secret`, by asserting on a captured logger
