# Q2394: validate — fallback never expires via blank old secret

## Question
Can an unprivileged attacker reach `HmacValidator.validate` through `ShopifyAPI::Utils::HmacValidator.validate`, the single arbiter of authenticity for both the OAuth callback and every inbound webhook while supplying an `old_api_secret_key` set to an empty or whitespace string, altering which branch runs, so that the `old_api_secret_key` branch has no cutoff, so a rotated secret remains a valid signing key forever, breaking the requirement that SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source, and ending in Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`)?

## Target
- File/function: `lib/shopify_api/utils/hmac_validator.rb` -> `HmacValidator.validate`
- Entrypoint: `ShopifyAPI::Utils::HmacValidator.validate`, the single arbiter of authenticity for both the OAuth callback and every inbound webhook
- Attacker controls: an `old_api_secret_key` set to an empty or whitespace string, altering which branch runs
- Exploit idea: the `old_api_secret_key` branch has no cutoff, so a rotated secret remains a valid signing key forever
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`) (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest: set `Context.old_api_secret_key`, sign under it, and assert `validate` accepts long after rotation
