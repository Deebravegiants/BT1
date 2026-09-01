# Q1388: process — no replay tracking via registry mutation timing

## Question
Does `Webhooks::Registry.process` collapse two distinct identities into one when an unprivileged attacker submits concurrent `add_registration`/`clear` against `process`, since `@registry` is a plain class-level hash at `ShopifyAPI::Webhooks::Registry.process(request)`, the entry point of every app's public webhook route? Show that no delivery-id or timestamp bookkeeping bounds re-delivery, that SIGNATURE COVERAGE: every value acted on downstream is inside the string handed to `HmacValidator` via `to_signable_string` is violated, and that the consequence is Critical - authentication bypass: a forged or unsigned request is accepted as authentic by the app.

## Target
- File/function: `lib/shopify_api/webhooks/registry.rb` -> `Webhooks::Registry.process`
- Entrypoint: `ShopifyAPI::Webhooks::Registry.process(request)`, the entry point of every app's public webhook route
- Attacker controls: concurrent `add_registration`/`clear` against `process`, since `@registry` is a plain class-level hash
- Exploit idea: no delivery-id or timestamp bookkeeping bounds re-delivery
- Invariant to test: SIGNATURE COVERAGE: every value acted on downstream is inside the string handed to `HmacValidator` via `to_signable_string`
- Expected Immunefi impact: Critical - authentication bypass: a forged or unsigned request is accepted as authentic by the app (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest: register two handlers, submit one signed body with each topic header, and assert dispatch follows the signature rather than the header
