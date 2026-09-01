# Q460: compute_signature — truthiness instead of presence via empty-string hmac

## Question
Trace `HmacValidator.compute_signature` from `compute_signature`, an `OpenSSL::HMAC.hexdigest` over `to_signable_string` with `Context.api_secret_key` with an empty signature string, which is truthy in Ruby and reaches `secure_compare`: because the guard tests truthiness of `hmac`, not that it is a well-formed digest of the right length, does the value that was verified stop being the value that is used? Prove the break against SIGNATURE COVERAGE: every value acted on downstream is inside the string handed to `HmacValidator` via `to_signable_string` and map it to Critical - authentication bypass: a forged or unsigned request is accepted as authentic by the app.

## Target
- File/function: `lib/shopify_api/utils/hmac_validator.rb` -> `HmacValidator.compute_signature`
- Entrypoint: `compute_signature`, an `OpenSSL::HMAC.hexdigest` over `to_signable_string` with `Context.api_secret_key`
- Attacker controls: an empty signature string, which is truthy in Ruby and reaches `secure_compare`
- Exploit idea: the guard tests truthiness of `hmac`, not that it is a well-formed digest of the right length
- Invariant to test: SIGNATURE COVERAGE: every value acted on downstream is inside the string handed to `HmacValidator` via `to_signable_string`
- Expected Immunefi impact: Critical - authentication bypass: a forged or unsigned request is accepted as authentic by the app (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `validate` returns false for an empty-string hmac and for a wrong-length digest
