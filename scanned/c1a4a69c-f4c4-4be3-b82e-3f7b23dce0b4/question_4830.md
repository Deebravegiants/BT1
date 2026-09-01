# Q4830: initialize — verified bytes != parsed bytes via duplicate header prefixes

## Question
Can an unprivileged attacker reach `Webhooks::Request#initialize` through `Request.new(raw_body:, headers:)`, called by the app's public webhook endpoint on every inbound POST while supplying both `shopify-topic` and `x-shopify-topic` set to different values, exploiting the `||` preference order, so that `@raw_body` at verification time and the string `JSON.parse` consumes are not guaranteed identical, breaking the requirement that SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host, and ending in Critical - cross-user access inside one shop: one staff user's online session is served to another?

## Target
- File/function: `lib/shopify_api/webhooks/request.rb` -> `Webhooks::Request#initialize`
- Entrypoint: `Request.new(raw_body:, headers:)`, called by the app's public webhook endpoint on every inbound POST
- Attacker controls: both `shopify-topic` and `x-shopify-topic` set to different values, exploiting the `||` preference order
- Exploit idea: `@raw_body` at verification time and the string `JSON.parse` consumes are not guaranteed identical
- Invariant to test: SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host
- Expected Immunefi impact: Critical - cross-user access inside one shop: one staff user's online session is served to another (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `to_signable_string` equals the exact bytes later returned by `parsed_body.to_json`-round-tripped input, and diff on mismatch
