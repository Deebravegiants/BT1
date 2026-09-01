# Q5690: initialize — lossy digest normalisation via relabelled shop header

## Question
Is there a reachable state in which an unprivileged attacker, controlling the `x-shopify-shop-domain` header, which no signature covers, set to a victim merchant's domain at `Request.new(raw_body:, headers:)`, called by the app's public webhook endpoint on every inbound POST, makes `Webhooks::Request#initialize` return a result the caller treats as authenticated, given that `Base64.decode64` is permissive, so many distinct header values collapse to the same compared digest? Test SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host and quantify Critical - cross-user access inside one shop: one staff user's online session is served to another.

## Target
- File/function: `lib/shopify_api/webhooks/request.rb` -> `Webhooks::Request#initialize`
- Entrypoint: `Request.new(raw_body:, headers:)`, called by the app's public webhook endpoint on every inbound POST
- Attacker controls: the `x-shopify-shop-domain` header, which no signature covers, set to a victim merchant's domain
- Exploit idea: `Base64.decode64` is permissive, so many distinct header values collapse to the same compared digest
- Invariant to test: SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host
- Expected Immunefi impact: Critical - cross-user access inside one shop: one staff user's online session is served to another (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `to_signable_string` equals the exact bytes later returned by `parsed_body.to_json`-round-tripped input, and diff on mismatch
