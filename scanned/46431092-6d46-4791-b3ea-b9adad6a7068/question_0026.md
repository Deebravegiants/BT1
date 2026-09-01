# Q26: Utils::VerifiableQuery — nilable signature via implementation divergence

## Question
Trace `Utils::VerifiableQuery` from the `VerifiableQuery` interface - `hmac` and `to_signable_string` - implemented by `AuthQuery` and `Webhooks::Request` with the two implementations, which cover very different amounts of the request (five query fields versus the raw body only): because an implementation returning nil makes `validate` return false, but callers that ignore the boolean proceed anyway, does the value that was verified stop being the value that is used? Prove the break against SIGNATURE COVERAGE: every value acted on downstream is inside the string handed to `HmacValidator` via `to_signable_string` and map it to Critical - authentication bypass: a forged or unsigned request is accepted as authentic by the app.

## Target
- File/function: `lib/shopify_api/utils/verifiable_query.rb` -> `Utils::VerifiableQuery`
- Entrypoint: the `VerifiableQuery` interface - `hmac` and `to_signable_string` - implemented by `AuthQuery` and `Webhooks::Request`
- Attacker controls: the two implementations, which cover very different amounts of the request (five query fields versus the raw body only)
- Exploit idea: an implementation returning nil makes `validate` return false, but callers that ignore the boolean proceed anyway
- Invariant to test: SIGNATURE COVERAGE: every value acted on downstream is inside the string handed to `HmacValidator` via `to_signable_string`
- Expected Immunefi impact: Critical - authentication bypass: a forged or unsigned request is accepted as authentic by the app (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest: assert every `VerifiableQuery` implementation's `to_signable_string` covers every field its consumers read
