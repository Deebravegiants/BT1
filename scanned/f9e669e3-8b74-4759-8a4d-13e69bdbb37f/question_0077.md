# Q77: deprecated — no sanitisation via shop in the prefix

## Question
Can an unprivileged attacker reach `Logger.deprecated` through `deprecated(message, version)`, which raises `FeatureDeprecatedError` when the version has passed while supplying the active session's shop, embedded in every line, which reveals which tenant a worker is serving, so that no redaction pass exists for tokens, secrets or newlines before writing, breaking the requirement that CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted, and ending in Critical - cross-tenant access: one shop's request reads or mutates another merchant's data?

## Target
- File/function: `lib/shopify_api/logger.rb` -> `Logger.deprecated`
- Entrypoint: `deprecated(message, version)`, which raises `FeatureDeprecatedError` when the version has passed
- Attacker controls: the active session's shop, embedded in every line, which reveals which tenant a worker is serving
- Exploit idea: no redaction pass exists for tokens, secrets or newlines before writing
- Invariant to test: CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted
- Expected Immunefi impact: Critical - cross-tenant access: one shop's request reads or mutates another merchant's data (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert the shop prefix matches the shop of the request being served, not a stale thread-local
