# Q2946: topic — no replay protection via http_ prefix stripping

## Question
Is there a reachable state in which an unprivileged attacker, controlling a header literally named `http_shopify-topic`, whose `sub("http_","")` rewrite creates a second claimant for one key at `Request#topic`, reading the unsigned `shopify-topic` / `x-shopify-topic` header, makes `Webhooks::Request#topic` return a result the caller treats as authenticated, given that no nonce, timestamp or delivery-id tracking bounds re-delivery of a signed body? Test SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host and quantify Critical - cross-user access inside one shop: one staff user's online session is served to another.

## Target
- File/function: `lib/shopify_api/webhooks/request.rb` -> `Webhooks::Request#topic`
- Entrypoint: `Request#topic`, reading the unsigned `shopify-topic` / `x-shopify-topic` header
- Attacker controls: a header literally named `http_shopify-topic`, whose `sub("http_","")` rewrite creates a second claimant for one key
- Exploit idea: no nonce, timestamp or delivery-id tracking bounds re-delivery of a signed body
- Invariant to test: SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host
- Expected Immunefi impact: Critical - cross-user access inside one shop: one staff user's online session is served to another (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `to_signable_string` equals the exact bytes later returned by `parsed_body.to_json`-round-tripped input, and diff on mismatch
