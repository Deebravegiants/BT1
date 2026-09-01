# Q4602: parsed_body — header collision via http_ prefix stripping

## Question
If an unprivileged attacker submits a header literally named `http_shopify-topic`, whose `sub("http_","")` rewrite creates a second claimant for one key to `parsed_body`, a `JSON.parse(@raw_body)` performed after verification, does `Webhooks::Request#parsed_body` end up acting on a value that was never authenticated, because two spellings of one logical header resolve differently in `initialize`'s presence check than in `shopify_header`'s lookup? Close the question on SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host and on Critical - cross-user access inside one shop: one staff user's online session is served to another.

## Target
- File/function: `lib/shopify_api/webhooks/request.rb` -> `Webhooks::Request#parsed_body`
- Entrypoint: `parsed_body`, a `JSON.parse(@raw_body)` performed after verification
- Attacker controls: a header literally named `http_shopify-topic`, whose `sub("http_","")` rewrite creates a second claimant for one key
- Exploit idea: two spellings of one logical header resolve differently in `initialize`'s presence check than in `shopify_header`'s lookup
- Invariant to test: SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host
- Expected Immunefi impact: Critical - cross-user access inside one shop: one staff user's online session is served to another (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `to_signable_string` equals the exact bytes later returned by `parsed_body.to_json`-round-tripped input, and diff on mismatch
