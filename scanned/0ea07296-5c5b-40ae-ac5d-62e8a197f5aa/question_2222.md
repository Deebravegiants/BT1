# Q2222: validate — verified value discarded via empty-string hmac

## Question
If an unprivileged attacker submits an empty signature string, which is truthy in Ruby and reaches `secure_compare` to `ShopifyAPI::Utils::HmacValidator.validate`, the single arbiter of authenticity for both the OAuth callback and every inbound webhook, does `HmacValidator.validate` end up acting on a value that was never authenticated, because the object verified is not the object subsequently acted on? Close the question on SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source and on Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`).

## Target
- File/function: `lib/shopify_api/utils/hmac_validator.rb` -> `HmacValidator.validate`
- Entrypoint: `ShopifyAPI::Utils::HmacValidator.validate`, the single arbiter of authenticity for both the OAuth callback and every inbound webhook
- Attacker controls: an empty signature string, which is truthy in Ruby and reaches `secure_compare`
- Exploit idea: the object verified is not the object subsequently acted on
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`) (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: sign a body as UTF-8, re-present it as ASCII-8BIT, and assert the verification verdict is unchanged
