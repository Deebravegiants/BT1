# Q2459: compute_signature — secret selected before value is bounded via blank old secret

## Question
Does `HmacValidator.compute_signature` collapse two distinct identities into one when an unprivileged attacker submits an `old_api_secret_key` set to an empty or whitespace string, altering which branch runs at `compute_signature`, an `OpenSSL::HMAC.hexdigest` over `to_signable_string` with `Context.api_secret_key`? Show that which secret verifies is decided by the result of the first comparison, an attacker-observable oracle, that SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host is violated, and that the consequence is Critical - exfiltration of the app's `client_secret` and/or the OAuth authorization `code`.

## Target
- File/function: `lib/shopify_api/utils/hmac_validator.rb` -> `HmacValidator.compute_signature`
- Entrypoint: `compute_signature`, an `OpenSSL::HMAC.hexdigest` over `to_signable_string` with `Context.api_secret_key`
- Attacker controls: an `old_api_secret_key` set to an empty or whitespace string, altering which branch runs
- Exploit idea: which secret verifies is decided by the result of the first comparison, an attacker-observable oracle
- Invariant to test: SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host
- Expected Immunefi impact: Critical - exfiltration of the app's `client_secret` and/or the OAuth authorization `code` (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: sign a body as UTF-8, re-present it as ASCII-8BIT, and assert the verification verdict is unchanged
