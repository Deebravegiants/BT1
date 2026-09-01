# Q1190: validate_signature — authenticity is not authorisation via case-varied digest

## Question
Can an unprivileged attacker reach `HmacValidator.validate_signature` through the private `validate_signature`, which calls `OpenSSL.secure_compare(computed_signature, received_signature)` while supplying an uppercase or mixed-case hex digest compared byte-wise against the lowercase `hexdigest` output, so that a valid signature proves Shopify signed something for some shop, not that it was for this shop, this browser or this topic, breaking the requirement that SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source, and ending in Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`)?

## Target
- File/function: `lib/shopify_api/utils/hmac_validator.rb` -> `HmacValidator.validate_signature`
- Entrypoint: the private `validate_signature`, which calls `OpenSSL.secure_compare(computed_signature, received_signature)`
- Attacker controls: an uppercase or mixed-case hex digest compared byte-wise against the lowercase `hexdigest` output
- Exploit idea: a valid signature proves Shopify signed something for some shop, not that it was for this shop, this browser or this topic
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`) (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: sign a body as UTF-8, re-present it as ASCII-8BIT, and assert the verification verdict is unchanged
