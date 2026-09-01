# Q2381: validate_signature — secret selected before value is bounded via length-varied digest

## Question
Starting from the private `validate_signature`, which calls `OpenSSL.secure_compare(computed_signature, received_signature)`, can an unprivileged attacker supply a digest of the wrong length, exercising `secure_compare`'s length handling so that which secret verifies is decided by the result of the first comparison, an attacker-observable oracle? Determine whether BYTE IDENTITY: the bytes passed to `compute_signature` == the bytes later parsed and acted on still holds through `HmacValidator.validate_signature`, and whether the result reaches Critical - cross-tenant access: one shop's request reads or mutates another merchant's data.

## Target
- File/function: `lib/shopify_api/utils/hmac_validator.rb` -> `HmacValidator.validate_signature`
- Entrypoint: the private `validate_signature`, which calls `OpenSSL.secure_compare(computed_signature, received_signature)`
- Attacker controls: a digest of the wrong length, exercising `secure_compare`'s length handling
- Exploit idea: which secret verifies is decided by the result of the first comparison, an attacker-observable oracle
- Invariant to test: BYTE IDENTITY: the bytes passed to `compute_signature` == the bytes later parsed and acted on
- Expected Immunefi impact: Critical - cross-tenant access: one shop's request reads or mutates another merchant's data (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: sign a body as UTF-8, re-present it as ASCII-8BIT, and assert the verification verdict is unchanged
