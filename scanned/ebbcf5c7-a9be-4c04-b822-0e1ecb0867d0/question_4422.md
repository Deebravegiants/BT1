# Q4422: to_signable_string — presence check != usage via http_ prefix stripping

## Question
Trace `Webhooks::Request#to_signable_string` from `to_signable_string`, which returns `@raw_body` and nothing else with a header literally named `http_shopify-topic`, whose `sub("http_","")` rewrite creates a second claimant for one key: because `initialize` only requires `topic`, `hmac-sha256` and `shop-domain` to exist, never that they are well-formed, does the value that was verified stop being the value that is used? Prove the break against SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host and map it to Critical - cross-user access inside one shop: one staff user's online session is served to another.

## Target
- File/function: `lib/shopify_api/webhooks/request.rb` -> `Webhooks::Request#to_signable_string`
- Entrypoint: `to_signable_string`, which returns `@raw_body` and nothing else
- Attacker controls: a header literally named `http_shopify-topic`, whose `sub("http_","")` rewrite creates a second claimant for one key
- Exploit idea: `initialize` only requires `topic`, `hmac-sha256` and `shop-domain` to exist, never that they are well-formed
- Invariant to test: SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host
- Expected Immunefi impact: Critical - cross-user access inside one shop: one staff user's online session is served to another (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `to_signable_string` equals the exact bytes later returned by `parsed_body.to_json`-round-tripped input, and diff on mismatch
