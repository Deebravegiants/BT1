# Q104: Utils::VerifiableQuery — interface fixes no coverage contract via nilable hmac

## Question
Is there a reachable state in which an unprivileged attacker, controlling the `T.nilable(String)` return of `hmac`, which lets an implementation return nil and short-circuit validation at the `VerifiableQuery` interface - `hmac` and `to_signable_string` - implemented by `AuthQuery` and `Webhooks::Request`, makes `Utils::VerifiableQuery` return a result the caller treats as authenticated, given that the interface guarantees only that a string exists, not that it covers every field consumers trust? Test SIGNATURE COVERAGE: every value acted on downstream is inside the string handed to `HmacValidator` via `to_signable_string` and quantify Critical - authentication bypass: a forged or unsigned request is accepted as authentic by the app.

## Target
- File/function: `lib/shopify_api/utils/verifiable_query.rb` -> `Utils::VerifiableQuery`
- Entrypoint: the `VerifiableQuery` interface - `hmac` and `to_signable_string` - implemented by `AuthQuery` and `Webhooks::Request`
- Attacker controls: the `T.nilable(String)` return of `hmac`, which lets an implementation return nil and short-circuit validation
- Exploit idea: the interface guarantees only that a string exists, not that it covers every field consumers trust
- Invariant to test: SIGNATURE COVERAGE: every value acted on downstream is inside the string handed to `HmacValidator` via `to_signable_string`
- Expected Immunefi impact: Critical - authentication bypass: a forged or unsigned request is accepted as authentic by the app (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest: assert every `VerifiableQuery` implementation's `to_signable_string` covers every field its consumers read
