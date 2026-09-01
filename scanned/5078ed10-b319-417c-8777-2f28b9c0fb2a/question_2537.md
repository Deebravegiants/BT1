# Q2537: validate — authenticity is not authorisation via case-varied digest

## Question
If an unprivileged attacker submits an uppercase or mixed-case hex digest compared byte-wise against the lowercase `hexdigest` output to `ShopifyAPI::Utils::HmacValidator.validate`, the single arbiter of authenticity for both the OAuth callback and every inbound webhook, does `HmacValidator.validate` end up acting on a value that was never authenticated, because a valid signature proves Shopify signed something for some shop, not that it was for this shop, this browser or this topic? Close the question on BYTE IDENTITY: the bytes passed to `compute_signature` == the bytes later parsed and acted on and on Critical - cross-tenant access: one shop's request reads or mutates another merchant's data.

## Target
- File/function: `lib/shopify_api/utils/hmac_validator.rb` -> `HmacValidator.validate`
- Entrypoint: `ShopifyAPI::Utils::HmacValidator.validate`, the single arbiter of authenticity for both the OAuth callback and every inbound webhook
- Attacker controls: an uppercase or mixed-case hex digest compared byte-wise against the lowercase `hexdigest` output
- Exploit idea: a valid signature proves Shopify signed something for some shop, not that it was for this shop, this browser or this topic
- Invariant to test: BYTE IDENTITY: the bytes passed to `compute_signature` == the bytes later parsed and acted on
- Expected Immunefi impact: Critical - cross-tenant access: one shop's request reads or mutates another merchant's data (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: sign a body as UTF-8, re-present it as ASCII-8BIT, and assert the verification verdict is unchanged
