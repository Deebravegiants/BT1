# Q2057: validate_signature — authenticity is not authorisation via empty-string hmac

## Question
Is there a reachable state in which an unprivileged attacker, controlling an empty signature string, which is truthy in Ruby and reaches `secure_compare` at the private `validate_signature`, which calls `OpenSSL.secure_compare(computed_signature, received_signature)`, makes `HmacValidator.validate_signature` return a result the caller treats as authenticated, given that a valid signature proves Shopify signed something for some shop, not that it was for this shop, this browser or this topic? Test BYTE IDENTITY: the bytes passed to `compute_signature` == the bytes later parsed and acted on and quantify Critical - cross-tenant access: one shop's request reads or mutates another merchant's data.

## Target
- File/function: `lib/shopify_api/utils/hmac_validator.rb` -> `HmacValidator.validate_signature`
- Entrypoint: the private `validate_signature`, which calls `OpenSSL.secure_compare(computed_signature, received_signature)`
- Attacker controls: an empty signature string, which is truthy in Ruby and reaches `secure_compare`
- Exploit idea: a valid signature proves Shopify signed something for some shop, not that it was for this shop, this browser or this topic
- Invariant to test: BYTE IDENTITY: the bytes passed to `compute_signature` == the bytes later parsed and acted on
- Expected Immunefi impact: Critical - cross-tenant access: one shop's request reads or mutates another merchant's data (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: sign a body as UTF-8, re-present it as ASCII-8BIT, and assert the verification verdict is unchanged
