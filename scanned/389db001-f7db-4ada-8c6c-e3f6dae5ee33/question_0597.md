# Q597: initialize — shop handed to handler unverified via relabelled topic header

## Question
Does `Webhooks::Request#initialize` collapse two distinct identities into one when an unprivileged attacker submits the `x-shopify-topic` header, which selects the handler in `Registry.process` at `Request.new(raw_body:, headers:)`, called by the app's public webhook endpoint on every inbound POST? Show that `WebhookMetadata#shop` is the raw header value and is what the host app uses to decide whose records to touch, that BYTE IDENTITY: the bytes passed to `compute_signature` == the bytes later parsed and acted on is violated, and that the consequence is Critical - cross-tenant access: one shop's request reads or mutates another merchant's data.

## Target
- File/function: `lib/shopify_api/webhooks/request.rb` -> `Webhooks::Request#initialize`
- Entrypoint: `Request.new(raw_body:, headers:)`, called by the app's public webhook endpoint on every inbound POST
- Attacker controls: the `x-shopify-topic` header, which selects the handler in `Registry.process`
- Exploit idea: `WebhookMetadata#shop` is the raw header value and is what the host app uses to decide whose records to touch
- Invariant to test: BYTE IDENTITY: the bytes passed to `compute_signature` == the bytes later parsed and acted on
- Expected Immunefi impact: Critical - cross-tenant access: one shop's request reads or mutates another merchant's data (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `Request#hmac` yields the same value for two different header strings, then assert `HmacValidator.validate` accepts both
