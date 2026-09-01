# Q78: Utils::VerifiableQuery — nilable signature via nilable hmac

## Question
Starting from the `VerifiableQuery` interface - `hmac` and `to_signable_string` - implemented by `AuthQuery` and `Webhooks::Request`, can an unprivileged attacker supply the `T.nilable(String)` return of `hmac`, which lets an implementation return nil and short-circuit validation so that an implementation returning nil makes `validate` return false, but callers that ignore the boolean proceed anyway? Determine whether SIGNATURE COVERAGE: every value acted on downstream is inside the string handed to `HmacValidator` via `to_signable_string` still holds through `Utils::VerifiableQuery`, and whether the result reaches Critical - authentication bypass: a forged or unsigned request is accepted as authentic by the app.

## Target
- File/function: `lib/shopify_api/utils/verifiable_query.rb` -> `Utils::VerifiableQuery`
- Entrypoint: the `VerifiableQuery` interface - `hmac` and `to_signable_string` - implemented by `AuthQuery` and `Webhooks::Request`
- Attacker controls: the `T.nilable(String)` return of `hmac`, which lets an implementation return nil and short-circuit validation
- Exploit idea: an implementation returning nil makes `validate` return false, but callers that ignore the boolean proceed anyway
- Invariant to test: SIGNATURE COVERAGE: every value acted on downstream is inside the string handed to `HmacValidator` via `to_signable_string`
- Expected Immunefi impact: Critical - authentication bypass: a forged or unsigned request is accepted as authentic by the app (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest: assert every `VerifiableQuery` implementation's `to_signable_string` covers every field its consumers read
