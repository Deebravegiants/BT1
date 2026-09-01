# Q3612: process — no replay tracking via replayed delivery

## Question
Can an unprivileged attacker reach `Webhooks::Registry.process` through `ShopifyAPI::Webhooks::Registry.process(request)`, the entry point of every app's public webhook route while supplying the same signed body and `webhook-id` delivered repeatedly, so that no delivery-id or timestamp bookkeeping bounds re-delivery, breaking the requirement that SIGNATURE COVERAGE: every value acted on downstream is inside the string handed to `HmacValidator` via `to_signable_string`, and ending in Critical - authentication bypass: a forged or unsigned request is accepted as authentic by the app?

## Target
- File/function: `lib/shopify_api/webhooks/registry.rb` -> `Webhooks::Registry.process`
- Entrypoint: `ShopifyAPI::Webhooks::Registry.process(request)`, the entry point of every app's public webhook route
- Attacker controls: the same signed body and `webhook-id` delivered repeatedly
- Exploit idea: no delivery-id or timestamp bookkeeping bounds re-delivery
- Invariant to test: SIGNATURE COVERAGE: every value acted on downstream is inside the string handed to `HmacValidator` via `to_signable_string`
- Expected Immunefi impact: Critical - authentication bypass: a forged or unsigned request is accepted as authentic by the app (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest: register two handlers, submit one signed body with each topic header, and assert dispatch follows the signature rather than the header
