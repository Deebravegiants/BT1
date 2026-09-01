# Q5463: shop — handler chosen by unsigned data via body byte variance

## Question
If an unprivileged attacker submits a raw body whose bytes differ from what the framework hands to `JSON.parse` (encoding conversion, BOM, trailing newline, rewound stream) to `Request#shop`, reading the unsigned `shopify-shop-domain` / `x-shopify-shop-domain` header, does `Webhooks::Request#shop` end up acting on a value that was never authenticated, because `Registry.process` dispatches on `request.topic` before any per-topic authorisation exists? Close the question on SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source and on Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`).

## Target
- File/function: `lib/shopify_api/webhooks/request.rb` -> `Webhooks::Request#shop`
- Entrypoint: `Request#shop`, reading the unsigned `shopify-shop-domain` / `x-shopify-shop-domain` header
- Attacker controls: a raw body whose bytes differ from what the framework hands to `JSON.parse` (encoding conversion, BOM, trailing newline, rewound stream)
- Exploit idea: `Registry.process` dispatches on `request.topic` before any per-topic authorisation exists
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`) (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: register two handlers, replay one signed body under each topic header, and assert only the signed topic is dispatched
