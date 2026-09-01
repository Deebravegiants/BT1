# Q313: validate_signature — encoding-dependent digest via length-varied digest

## Question
Trace `HmacValidator.validate_signature` from the private `validate_signature`, which calls `OpenSSL.secure_compare(computed_signature, received_signature)` with a digest of the wrong length, exercising `secure_compare`'s length handling: because `hexdigest` over a differently-encoded string yields a different digest for the same logical content, does the value that was verified stop being the value that is used? Prove the break against BYTE IDENTITY: the bytes passed to `compute_signature` == the bytes later parsed and acted on and map it to Critical - cross-tenant access: one shop's request reads or mutates another merchant's data.

## Target
- File/function: `lib/shopify_api/utils/hmac_validator.rb` -> `HmacValidator.validate_signature`
- Entrypoint: the private `validate_signature`, which calls `OpenSSL.secure_compare(computed_signature, received_signature)`
- Attacker controls: a digest of the wrong length, exercising `secure_compare`'s length handling
- Exploit idea: `hexdigest` over a differently-encoded string yields a different digest for the same logical content
- Invariant to test: BYTE IDENTITY: the bytes passed to `compute_signature` == the bytes later parsed and acted on
- Expected Immunefi impact: Critical - cross-tenant access: one shop's request reads or mutates another merchant's data (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `validate` returns false for an empty-string hmac and for a wrong-length digest
