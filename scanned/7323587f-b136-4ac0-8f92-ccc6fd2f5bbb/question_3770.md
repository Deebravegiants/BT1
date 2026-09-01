# Q3770: parsed_body — verified bytes != parsed bytes via omitted optional headers

## Question
Can an omitted `x-shopify-api-version` or `x-shopify-webhook-id`, which `initialize` never requires but the accessors `T.cast` to String, supplied by an unprivileged attacker at `parsed_body`, a `JSON.parse(@raw_body)` performed after verification, make `Webhooks::Request#parsed_body` and the code consuming its result disagree, given that `@raw_body` at verification time and the string `JSON.parse` consumes are not guaranteed identical? The binding to test is SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host; the impact to prove is Critical - cross-user access inside one shop: one staff user's online session is served to another.

## Target
- File/function: `lib/shopify_api/webhooks/request.rb` -> `Webhooks::Request#parsed_body`
- Entrypoint: `parsed_body`, a `JSON.parse(@raw_body)` performed after verification
- Attacker controls: an omitted `x-shopify-api-version` or `x-shopify-webhook-id`, which `initialize` never requires but the accessors `T.cast` to String
- Exploit idea: `@raw_body` at verification time and the string `JSON.parse` consumes are not guaranteed identical
- Invariant to test: SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host
- Expected Immunefi impact: Critical - cross-user access inside one shop: one staff user's online session is served to another (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `to_signable_string` equals the exact bytes later returned by `parsed_body.to_json`-round-tripped input, and diff on mismatch
