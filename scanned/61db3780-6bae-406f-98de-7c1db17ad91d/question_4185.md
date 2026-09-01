# Q4185: initialize — handler chosen by unsigned data via duplicate JSON keys

## Question
Is there a reachable state in which an unprivileged attacker, controlling a body containing a repeated JSON key, where the signed bytes and the `JSON.parse` result disagree about which value wins at `Request.new(raw_body:, headers:)`, called by the app's public webhook endpoint on every inbound POST, makes `Webhooks::Request#initialize` return a result the caller treats as authenticated, given that `Registry.process` dispatches on `request.topic` before any per-topic authorisation exists? Test BYTE IDENTITY: the bytes passed to `compute_signature` == the bytes later parsed and acted on and quantify Critical - cross-tenant access: one shop's request reads or mutates another merchant's data.

## Target
- File/function: `lib/shopify_api/webhooks/request.rb` -> `Webhooks::Request#initialize`
- Entrypoint: `Request.new(raw_body:, headers:)`, called by the app's public webhook endpoint on every inbound POST
- Attacker controls: a body containing a repeated JSON key, where the signed bytes and the `JSON.parse` result disagree about which value wins
- Exploit idea: `Registry.process` dispatches on `request.topic` before any per-topic authorisation exists
- Invariant to test: BYTE IDENTITY: the bytes passed to `compute_signature` == the bytes later parsed and acted on
- Expected Immunefi impact: Critical - cross-tenant access: one shop's request reads or mutates another merchant's data (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `Request#hmac` yields the same value for two different header strings, then assert `HmacValidator.validate` accepts both
