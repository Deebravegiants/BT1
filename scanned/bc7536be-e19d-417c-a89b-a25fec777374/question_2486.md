# Q2486: shopify_header — shop handed to handler unverified via base64 padding variants

## Question
Starting from the private `shopify_header`, which prefers `shopify-<name>` over `x-shopify-<name>`, can an unprivileged attacker supply an hmac header with altered padding, whitespace or non-alphabet characters that `Base64.decode64` silently drops so that `WebhookMetadata#shop` is the raw header value and is what the host app uses to decide whose records to touch? Determine whether SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host still holds through `Webhooks::Request#shopify_header`, and whether the result reaches Critical - cross-user access inside one shop: one staff user's online session is served to another.

## Target
- File/function: `lib/shopify_api/webhooks/request.rb` -> `Webhooks::Request#shopify_header`
- Entrypoint: the private `shopify_header`, which prefers `shopify-<name>` over `x-shopify-<name>`
- Attacker controls: an hmac header with altered padding, whitespace or non-alphabet characters that `Base64.decode64` silently drops
- Exploit idea: `WebhookMetadata#shop` is the raw header value and is what the host app uses to decide whose records to touch
- Invariant to test: SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host
- Expected Immunefi impact: Critical - cross-user access inside one shop: one staff user's online session is served to another (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `to_signable_string` equals the exact bytes later returned by `parsed_body.to_json`-round-tripped input, and diff on mismatch
