# Q3254: shop — header collision via base64 padding variants

## Question
Is there a reachable state in which an unprivileged attacker, controlling an hmac header with altered padding, whitespace or non-alphabet characters that `Base64.decode64` silently drops at `Request#shop`, reading the unsigned `shopify-shop-domain` / `x-shopify-shop-domain` header, makes `Webhooks::Request#shop` return a result the caller treats as authenticated, given that two spellings of one logical header resolve differently in `initialize`'s presence check than in `shopify_header`'s lookup? Test SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host and quantify Critical - cross-user access inside one shop: one staff user's online session is served to another.

## Target
- File/function: `lib/shopify_api/webhooks/request.rb` -> `Webhooks::Request#shop`
- Entrypoint: `Request#shop`, reading the unsigned `shopify-shop-domain` / `x-shopify-shop-domain` header
- Attacker controls: an hmac header with altered padding, whitespace or non-alphabet characters that `Base64.decode64` silently drops
- Exploit idea: two spellings of one logical header resolve differently in `initialize`'s presence check than in `shopify_header`'s lookup
- Invariant to test: SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host
- Expected Immunefi impact: Critical - cross-user access inside one shop: one staff user's online session is served to another (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `to_signable_string` equals the exact bytes later returned by `parsed_body.to_json`-round-tripped input, and diff on mismatch
