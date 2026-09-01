# Q3670: parsed_body — header collision via api-version header

## Question
Does `Webhooks::Request#parsed_body` collapse two distinct identities into one when an unprivileged attacker submits the unsigned `x-shopify-api-version` header, passed straight into `WebhookMetadata` at `parsed_body`, a `JSON.parse(@raw_body)` performed after verification? Show that two spellings of one logical header resolve differently in `initialize`'s presence check than in `shopify_header`'s lookup, that SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host is violated, and that the consequence is Critical - cross-user access inside one shop: one staff user's online session is served to another.

## Target
- File/function: `lib/shopify_api/webhooks/request.rb` -> `Webhooks::Request#parsed_body`
- Entrypoint: `parsed_body`, a `JSON.parse(@raw_body)` performed after verification
- Attacker controls: the unsigned `x-shopify-api-version` header, passed straight into `WebhookMetadata`
- Exploit idea: two spellings of one logical header resolve differently in `initialize`'s presence check than in `shopify_header`'s lookup
- Invariant to test: SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host
- Expected Immunefi impact: Critical - cross-user access inside one shop: one staff user's online session is served to another (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `to_signable_string` equals the exact bytes later returned by `parsed_body.to_json`-round-tripped input, and diff on mismatch
