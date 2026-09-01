# Q1118: validate_signature — verified value discarded via shared-secret multi-tenant

## Question
Trace `HmacValidator.validate_signature` from the private `validate_signature`, which calls `OpenSSL.secure_compare(computed_signature, received_signature)` with a validly signed artefact from the attacker's own shop, since one `api_secret_key` covers every shop that installed the app: because the object verified is not the object subsequently acted on, does the value that was verified stop being the value that is used? Prove the break against SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source and map it to Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`).

## Target
- File/function: `lib/shopify_api/utils/hmac_validator.rb` -> `HmacValidator.validate_signature`
- Entrypoint: the private `validate_signature`, which calls `OpenSSL.secure_compare(computed_signature, received_signature)`
- Attacker controls: a validly signed artefact from the attacker's own shop, since one `api_secret_key` covers every shop that installed the app
- Exploit idea: the object verified is not the object subsequently acted on
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`) (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: sign a body as UTF-8, re-present it as ASCII-8BIT, and assert the verification verdict is unchanged
