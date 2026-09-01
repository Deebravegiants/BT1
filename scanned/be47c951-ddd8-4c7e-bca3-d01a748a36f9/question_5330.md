# Q5330: shop — signature covers body only via body byte variance

## Question
If an unprivileged attacker submits a raw body whose bytes differ from what the framework hands to `JSON.parse` (encoding conversion, BOM, trailing newline, rewound stream) to `Request#shop`, reading the unsigned `shopify-shop-domain` / `x-shopify-shop-domain` header, does `Webhooks::Request#shop` end up acting on a value that was never authenticated, because `to_signable_string` returns `@raw_body`, so topic, shop, api-version and webhook-id are unauthenticated input travelling with a valid HMAC? Close the question on SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host and on Critical - cross-user access inside one shop: one staff user's online session is served to another.

## Target
- File/function: `lib/shopify_api/webhooks/request.rb` -> `Webhooks::Request#shop`
- Entrypoint: `Request#shop`, reading the unsigned `shopify-shop-domain` / `x-shopify-shop-domain` header
- Attacker controls: a raw body whose bytes differ from what the framework hands to `JSON.parse` (encoding conversion, BOM, trailing newline, rewound stream)
- Exploit idea: `to_signable_string` returns `@raw_body`, so topic, shop, api-version and webhook-id are unauthenticated input travelling with a valid HMAC
- Invariant to test: SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host
- Expected Immunefi impact: Critical - cross-user access inside one shop: one staff user's online session is served to another (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `to_signable_string` equals the exact bytes later returned by `parsed_body.to_json`-round-tripped input, and diff on mismatch
