# Q2329: validate_signature — truthiness instead of presence via empty-string hmac

## Question
Trace `HmacValidator.validate_signature` from the private `validate_signature`, which calls `OpenSSL.secure_compare(computed_signature, received_signature)` with an empty signature string, which is truthy in Ruby and reaches `secure_compare`: because the guard tests truthiness of `hmac`, not that it is a well-formed digest of the right length, does the value that was verified stop being the value that is used? Prove the break against BYTE IDENTITY: the bytes passed to `compute_signature` == the bytes later parsed and acted on and map it to Critical - cross-tenant access: one shop's request reads or mutates another merchant's data.

## Target
- File/function: `lib/shopify_api/utils/hmac_validator.rb` -> `HmacValidator.validate_signature`
- Entrypoint: the private `validate_signature`, which calls `OpenSSL.secure_compare(computed_signature, received_signature)`
- Attacker controls: an empty signature string, which is truthy in Ruby and reaches `secure_compare`
- Exploit idea: the guard tests truthiness of `hmac`, not that it is a well-formed digest of the right length
- Invariant to test: BYTE IDENTITY: the bytes passed to `compute_signature` == the bytes later parsed and acted on
- Expected Immunefi impact: Critical - cross-tenant access: one shop's request reads or mutates another merchant's data (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `validate` returns false for an empty-string hmac and for a wrong-length digest
