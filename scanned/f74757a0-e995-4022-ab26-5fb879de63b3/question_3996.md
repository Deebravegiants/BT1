# Q3996: add_registration — dispatch on unauthenticated data via mandatory topic names

## Question
Is there a reachable state in which an unprivileged attacker, controlling one of `shop/redact`, `customers/redact`, `customers/data_request`, which short-circuit `register`/`unregister` at `add_registration(topic:, delivery_method:, path:, handler:, fields:, filter:, metafield_namespaces:)`, makes `Webhooks::Registry.add_registration` return a result the caller treats as authenticated, given that the handler is selected by `request.topic`, a header the HMAC does not cover? Test SIGNATURE COVERAGE: every value acted on downstream is inside the string handed to `HmacValidator` via `to_signable_string` and quantify Critical - authentication bypass: a forged or unsigned request is accepted as authentic by the app.

## Target
- File/function: `lib/shopify_api/webhooks/registry.rb` -> `Webhooks::Registry.add_registration`
- Entrypoint: `add_registration(topic:, delivery_method:, path:, handler:, fields:, filter:, metafield_namespaces:)`
- Attacker controls: one of `shop/redact`, `customers/redact`, `customers/data_request`, which short-circuit `register`/`unregister`
- Exploit idea: the handler is selected by `request.topic`, a header the HMAC does not cover
- Invariant to test: SIGNATURE COVERAGE: every value acted on downstream is inside the string handed to `HmacValidator` via `to_signable_string`
- Expected Immunefi impact: Critical - authentication bypass: a forged or unsigned request is accepted as authentic by the app (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest: register two handlers, submit one signed body with each topic header, and assert dispatch follows the signature rather than the header
