# Q1998: hmac — header collision via replayed webhook-id

## Question
If an unprivileged attacker submits a repeated `x-shopify-webhook-id`, since nothing tracks delivery ids to `Request#hmac`, which returns `Digest.hexencode(Base64.decode64(header))` for the `x-shopify-hmac-sha256` header, does `Webhooks::Request#hmac` end up acting on a value that was never authenticated, because two spellings of one logical header resolve differently in `initialize`'s presence check than in `shopify_header`'s lookup? Close the question on SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host and on Critical - cross-user access inside one shop: one staff user's online session is served to another.

## Target
- File/function: `lib/shopify_api/webhooks/request.rb` -> `Webhooks::Request#hmac`
- Entrypoint: `Request#hmac`, which returns `Digest.hexencode(Base64.decode64(header))` for the `x-shopify-hmac-sha256` header
- Attacker controls: a repeated `x-shopify-webhook-id`, since nothing tracks delivery ids
- Exploit idea: two spellings of one logical header resolve differently in `initialize`'s presence check than in `shopify_header`'s lookup
- Invariant to test: SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host
- Expected Immunefi impact: Critical - cross-user access inside one shop: one staff user's online session is served to another (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `to_signable_string` equals the exact bytes later returned by `parsed_body.to_json`-round-tripped input, and diff on mismatch
