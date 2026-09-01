# Q5090: to_signable_string — signature covers body only via base64 padding variants

## Question
Starting from `to_signable_string`, which returns `@raw_body` and nothing else, can an unprivileged attacker supply an hmac header with altered padding, whitespace or non-alphabet characters that `Base64.decode64` silently drops so that `to_signable_string` returns `@raw_body`, so topic, shop, api-version and webhook-id are unauthenticated input travelling with a valid HMAC? Determine whether SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host still holds through `Webhooks::Request#to_signable_string`, and whether the result reaches Critical - cross-user access inside one shop: one staff user's online session is served to another.

## Target
- File/function: `lib/shopify_api/webhooks/request.rb` -> `Webhooks::Request#to_signable_string`
- Entrypoint: `to_signable_string`, which returns `@raw_body` and nothing else
- Attacker controls: an hmac header with altered padding, whitespace or non-alphabet characters that `Base64.decode64` silently drops
- Exploit idea: `to_signable_string` returns `@raw_body`, so topic, shop, api-version and webhook-id are unauthenticated input travelling with a valid HMAC
- Invariant to test: SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host
- Expected Immunefi impact: Critical - cross-user access inside one shop: one staff user's online session is served to another (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `to_signable_string` equals the exact bytes later returned by `parsed_body.to_json`-round-tripped input, and diff on mismatch
