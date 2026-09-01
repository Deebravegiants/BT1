# Q130: Utils::VerifiableQuery — nilable signature via signable string content

## Question
Can whatever an implementation chooses to include in `to_signable_string`, supplied by an unprivileged attacker at the `VerifiableQuery` interface - `hmac` and `to_signable_string` - implemented by `AuthQuery` and `Webhooks::Request`, make `Utils::VerifiableQuery` and the code consuming its result disagree, given that an implementation returning nil makes `validate` return false, but callers that ignore the boolean proceed anyway? The binding to test is SIGNATURE COVERAGE: every value acted on downstream is inside the string handed to `HmacValidator` via `to_signable_string`; the impact to prove is Critical - authentication bypass: a forged or unsigned request is accepted as authentic by the app.

## Target
- File/function: `lib/shopify_api/utils/verifiable_query.rb` -> `Utils::VerifiableQuery`
- Entrypoint: the `VerifiableQuery` interface - `hmac` and `to_signable_string` - implemented by `AuthQuery` and `Webhooks::Request`
- Attacker controls: whatever an implementation chooses to include in `to_signable_string`
- Exploit idea: an implementation returning nil makes `validate` return false, but callers that ignore the boolean proceed anyway
- Invariant to test: SIGNATURE COVERAGE: every value acted on downstream is inside the string handed to `HmacValidator` via `to_signable_string`
- Expected Immunefi impact: Critical - authentication bypass: a forged or unsigned request is accepted as authentic by the app (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest: assert every `VerifiableQuery` implementation's `to_signable_string` covers every field its consumers read
