# Q234: Utils::VerifiableQuery — no canonicalisation requirement via nilable hmac

## Question
If an unprivileged attacker submits the `T.nilable(String)` return of `hmac`, which lets an implementation return nil and short-circuit validation to the `VerifiableQuery` interface - `hmac` and `to_signable_string` - implemented by `AuthQuery` and `Webhooks::Request`, does `Utils::VerifiableQuery` end up acting on a value that was never authenticated, because nothing requires the signable string to be a canonical, unambiguous encoding? Close the question on SIGNATURE COVERAGE: every value acted on downstream is inside the string handed to `HmacValidator` via `to_signable_string` and on Critical - authentication bypass: a forged or unsigned request is accepted as authentic by the app.

## Target
- File/function: `lib/shopify_api/utils/verifiable_query.rb` -> `Utils::VerifiableQuery`
- Entrypoint: the `VerifiableQuery` interface - `hmac` and `to_signable_string` - implemented by `AuthQuery` and `Webhooks::Request`
- Attacker controls: the `T.nilable(String)` return of `hmac`, which lets an implementation return nil and short-circuit validation
- Exploit idea: nothing requires the signable string to be a canonical, unambiguous encoding
- Invariant to test: SIGNATURE COVERAGE: every value acted on downstream is inside the string handed to `HmacValidator` via `to_signable_string`
- Expected Immunefi impact: Critical - authentication bypass: a forged or unsigned request is accepted as authentic by the app (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest: assert every `VerifiableQuery` implementation's `to_signable_string` covers every field its consumers read
