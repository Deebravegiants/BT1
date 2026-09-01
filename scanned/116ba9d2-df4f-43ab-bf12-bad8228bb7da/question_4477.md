# Q4477: initialize — no replay protection via own-shop signed body

## Question
Can a body validly signed for the attacker's own shop and replayed with different headers, supplied by an unprivileged attacker at `Request.new(raw_body:, headers:)`, called by the app's public webhook endpoint on every inbound POST, make `Webhooks::Request#initialize` and the code consuming its result disagree, given that no nonce, timestamp or delivery-id tracking bounds re-delivery of a signed body? The binding to test is BYTE IDENTITY: the bytes passed to `compute_signature` == the bytes later parsed and acted on; the impact to prove is Critical - cross-tenant access: one shop's request reads or mutates another merchant's data.

## Target
- File/function: `lib/shopify_api/webhooks/request.rb` -> `Webhooks::Request#initialize`
- Entrypoint: `Request.new(raw_body:, headers:)`, called by the app's public webhook endpoint on every inbound POST
- Attacker controls: a body validly signed for the attacker's own shop and replayed with different headers
- Exploit idea: no nonce, timestamp or delivery-id tracking bounds re-delivery of a signed body
- Invariant to test: BYTE IDENTITY: the bytes passed to `compute_signature` == the bytes later parsed and acted on
- Expected Immunefi impact: Critical - cross-tenant access: one shop's request reads or mutates another merchant's data (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `Request#hmac` yields the same value for two different header strings, then assert `HmacValidator.validate` accepts both
