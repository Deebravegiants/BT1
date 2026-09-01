# Q4750: shop — shop handed to handler unverified via base64url vs standard

## Question
Can a base64url-encoded digest (`-`/`_`) that `decode64` reinterprets, supplied by an unprivileged attacker at `Request#shop`, reading the unsigned `shopify-shop-domain` / `x-shopify-shop-domain` header, make `Webhooks::Request#shop` and the code consuming its result disagree, given that `WebhookMetadata#shop` is the raw header value and is what the host app uses to decide whose records to touch? The binding to test is SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host; the impact to prove is Critical - cross-user access inside one shop: one staff user's online session is served to another.

## Target
- File/function: `lib/shopify_api/webhooks/request.rb` -> `Webhooks::Request#shop`
- Entrypoint: `Request#shop`, reading the unsigned `shopify-shop-domain` / `x-shopify-shop-domain` header
- Attacker controls: a base64url-encoded digest (`-`/`_`) that `decode64` reinterprets
- Exploit idea: `WebhookMetadata#shop` is the raw header value and is what the host app uses to decide whose records to touch
- Invariant to test: SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host
- Expected Immunefi impact: Critical - cross-user access inside one shop: one staff user's online session is served to another (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `to_signable_string` equals the exact bytes later returned by `parsed_body.to_json`-round-tripped input, and diff on mismatch
