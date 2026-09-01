# Q2485: validate_signature — fallback never expires via shared-secret multi-tenant

## Question
Can an unprivileged attacker reach `HmacValidator.validate_signature` through the private `validate_signature`, which calls `OpenSSL.secure_compare(computed_signature, received_signature)` while supplying a validly signed artefact from the attacker's own shop, since one `api_secret_key` covers every shop that installed the app, so that the `old_api_secret_key` branch has no cutoff, so a rotated secret remains a valid signing key forever, breaking the requirement that BYTE IDENTITY: the bytes passed to `compute_signature` == the bytes later parsed and acted on, and ending in Critical - cross-tenant access: one shop's request reads or mutates another merchant's data?

## Target
- File/function: `lib/shopify_api/utils/hmac_validator.rb` -> `HmacValidator.validate_signature`
- Entrypoint: the private `validate_signature`, which calls `OpenSSL.secure_compare(computed_signature, received_signature)`
- Attacker controls: a validly signed artefact from the attacker's own shop, since one `api_secret_key` covers every shop that installed the app
- Exploit idea: the `old_api_secret_key` branch has no cutoff, so a rotated secret remains a valid signing key forever
- Invariant to test: BYTE IDENTITY: the bytes passed to `compute_signature` == the bytes later parsed and acted on
- Expected Immunefi impact: Critical - cross-tenant access: one shop's request reads or mutates another merchant's data (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `validate` returns false for an empty-string hmac and for a wrong-length digest
