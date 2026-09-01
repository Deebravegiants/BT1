# Q2851: shop — lossy digest normalisation via body byte variance

## Question
Does `Webhooks::Request#shop` collapse two distinct identities into one when an unprivileged attacker submits a raw body whose bytes differ from what the framework hands to `JSON.parse` (encoding conversion, BOM, trailing newline, rewound stream) at `Request#shop`, reading the unsigned `shopify-shop-domain` / `x-shopify-shop-domain` header? Show that `Base64.decode64` is permissive, so many distinct header values collapse to the same compared digest, that SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source is violated, and that the consequence is Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`).

## Target
- File/function: `lib/shopify_api/webhooks/request.rb` -> `Webhooks::Request#shop`
- Entrypoint: `Request#shop`, reading the unsigned `shopify-shop-domain` / `x-shopify-shop-domain` header
- Attacker controls: a raw body whose bytes differ from what the framework hands to `JSON.parse` (encoding conversion, BOM, trailing newline, rewound stream)
- Exploit idea: `Base64.decode64` is permissive, so many distinct header values collapse to the same compared digest
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`) (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: register two handlers, replay one signed body under each topic header, and assert only the signed topic is dispatched
