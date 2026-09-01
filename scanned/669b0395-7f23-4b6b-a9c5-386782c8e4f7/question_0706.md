# Q706: validate_signature — encoding-dependent digest via case-varied digest

## Question
Is there a reachable state in which an unprivileged attacker, controlling an uppercase or mixed-case hex digest compared byte-wise against the lowercase `hexdigest` output at the private `validate_signature`, which calls `OpenSSL.secure_compare(computed_signature, received_signature)`, makes `HmacValidator.validate_signature` return a result the caller treats as authenticated, given that `hexdigest` over a differently-encoded string yields a different digest for the same logical content? Test SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source and quantify Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`).

## Target
- File/function: `lib/shopify_api/utils/hmac_validator.rb` -> `HmacValidator.validate_signature`
- Entrypoint: the private `validate_signature`, which calls `OpenSSL.secure_compare(computed_signature, received_signature)`
- Attacker controls: an uppercase or mixed-case hex digest compared byte-wise against the lowercase `hexdigest` output
- Exploit idea: `hexdigest` over a differently-encoded string yields a different digest for the same logical content
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`) (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `validate` returns false for an empty-string hmac and for a wrong-length digest
