# Q2117: validate — truthiness instead of presence via empty-string hmac

## Question
If an unprivileged attacker submits an empty signature string, which is truthy in Ruby and reaches `secure_compare` to `ShopifyAPI::Utils::HmacValidator.validate`, the single arbiter of authenticity for both the OAuth callback and every inbound webhook, does `HmacValidator.validate` end up acting on a value that was never authenticated, because the guard tests truthiness of `hmac`, not that it is a well-formed digest of the right length? Close the question on BYTE IDENTITY: the bytes passed to `compute_signature` == the bytes later parsed and acted on and on Critical - cross-tenant access: one shop's request reads or mutates another merchant's data.

## Target
- File/function: `lib/shopify_api/utils/hmac_validator.rb` -> `HmacValidator.validate`
- Entrypoint: `ShopifyAPI::Utils::HmacValidator.validate`, the single arbiter of authenticity for both the OAuth callback and every inbound webhook
- Attacker controls: an empty signature string, which is truthy in Ruby and reaches `secure_compare`
- Exploit idea: the guard tests truthiness of `hmac`, not that it is a well-formed digest of the right length
- Invariant to test: BYTE IDENTITY: the bytes passed to `compute_signature` == the bytes later parsed and acted on
- Expected Immunefi impact: Critical - cross-tenant access: one shop's request reads or mutates another merchant's data (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: sign a body as UTF-8, re-present it as ASCII-8BIT, and assert the verification verdict is unchanged
