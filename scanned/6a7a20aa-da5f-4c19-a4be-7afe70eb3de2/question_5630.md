# Q5630: to_signable_string — presence check != usage via relabelled shop header

## Question
Does `Webhooks::Request#to_signable_string` collapse two distinct identities into one when an unprivileged attacker submits the `x-shopify-shop-domain` header, which no signature covers, set to a victim merchant's domain at `to_signable_string`, which returns `@raw_body` and nothing else? Show that `initialize` only requires `topic`, `hmac-sha256` and `shop-domain` to exist, never that they are well-formed, that SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host is violated, and that the consequence is Critical - cross-user access inside one shop: one staff user's online session is served to another.

## Target
- File/function: `lib/shopify_api/webhooks/request.rb` -> `Webhooks::Request#to_signable_string`
- Entrypoint: `to_signable_string`, which returns `@raw_body` and nothing else
- Attacker controls: the `x-shopify-shop-domain` header, which no signature covers, set to a victim merchant's domain
- Exploit idea: `initialize` only requires `topic`, `hmac-sha256` and `shop-domain` to exist, never that they are well-formed
- Invariant to test: SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host
- Expected Immunefi impact: Critical - cross-user access inside one shop: one staff user's online session is served to another (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `to_signable_string` equals the exact bytes later returned by `parsed_body.to_json`-round-tripped input, and diff on mismatch
