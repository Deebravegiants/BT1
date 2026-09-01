# Q3956: process — dispatch on unauthenticated data via unsigned topic header

## Question
Starting from `ShopifyAPI::Webhooks::Registry.process(request)`, the entry point of every app's public webhook route, can an unprivileged attacker supply the topic, taken from an unsigned header, used both to select the handler and to build GraphQL documents so that the handler is selected by `request.topic`, a header the HMAC does not cover? Determine whether SIGNATURE COVERAGE: every value acted on downstream is inside the string handed to `HmacValidator` via `to_signable_string` still holds through `Webhooks::Registry.process`, and whether the result reaches Critical - authentication bypass: a forged or unsigned request is accepted as authentic by the app.

## Target
- File/function: `lib/shopify_api/webhooks/registry.rb` -> `Webhooks::Registry.process`
- Entrypoint: `ShopifyAPI::Webhooks::Registry.process(request)`, the entry point of every app's public webhook route
- Attacker controls: the topic, taken from an unsigned header, used both to select the handler and to build GraphQL documents
- Exploit idea: the handler is selected by `request.topic`, a header the HMAC does not cover
- Invariant to test: SIGNATURE COVERAGE: every value acted on downstream is inside the string handed to `HmacValidator` via `to_signable_string`
- Expected Immunefi impact: Critical - authentication bypass: a forged or unsigned request is accepted as authentic by the app (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest: register two handlers, submit one signed body with each topic header, and assert dispatch follows the signature rather than the header
