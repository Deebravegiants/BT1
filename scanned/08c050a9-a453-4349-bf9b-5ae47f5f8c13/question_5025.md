# Q5025: parsed_body — presence check != usage via replayed webhook-id

## Question
Is there a reachable state in which an unprivileged attacker, controlling a repeated `x-shopify-webhook-id`, since nothing tracks delivery ids at `parsed_body`, a `JSON.parse(@raw_body)` performed after verification, makes `Webhooks::Request#parsed_body` return a result the caller treats as authenticated, given that `initialize` only requires `topic`, `hmac-sha256` and `shop-domain` to exist, never that they are well-formed? Test BYTE IDENTITY: the bytes passed to `compute_signature` == the bytes later parsed and acted on and quantify Critical - cross-tenant access: one shop's request reads or mutates another merchant's data.

## Target
- File/function: `lib/shopify_api/webhooks/request.rb` -> `Webhooks::Request#parsed_body`
- Entrypoint: `parsed_body`, a `JSON.parse(@raw_body)` performed after verification
- Attacker controls: a repeated `x-shopify-webhook-id`, since nothing tracks delivery ids
- Exploit idea: `initialize` only requires `topic`, `hmac-sha256` and `shop-domain` to exist, never that they are well-formed
- Invariant to test: BYTE IDENTITY: the bytes passed to `compute_signature` == the bytes later parsed and acted on
- Expected Immunefi impact: Critical - cross-tenant access: one shop's request reads or mutates another merchant's data (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `Request#hmac` yields the same value for two different header strings, then assert `HmacValidator.validate` accepts both
