# Q314: initialize — shop handed to handler unverified via api-version header

## Question
Is there a reachable state in which an unprivileged attacker, controlling the unsigned `x-shopify-api-version` header, passed straight into `WebhookMetadata` at `Request.new(raw_body:, headers:)`, called by the app's public webhook endpoint on every inbound POST, makes `Webhooks::Request#initialize` return a result the caller treats as authenticated, given that `WebhookMetadata#shop` is the raw header value and is what the host app uses to decide whose records to touch? Test SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host and quantify Critical - cross-user access inside one shop: one staff user's online session is served to another.

## Target
- File/function: `lib/shopify_api/webhooks/request.rb` -> `Webhooks::Request#initialize`
- Entrypoint: `Request.new(raw_body:, headers:)`, called by the app's public webhook endpoint on every inbound POST
- Attacker controls: the unsigned `x-shopify-api-version` header, passed straight into `WebhookMetadata`
- Exploit idea: `WebhookMetadata#shop` is the raw header value and is what the host app uses to decide whose records to touch
- Invariant to test: SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host
- Expected Immunefi impact: Critical - cross-user access inside one shop: one staff user's online session is served to another (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `to_signable_string` equals the exact bytes later returned by `parsed_body.to_json`-round-tripped input, and diff on mismatch
