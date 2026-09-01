# Q5160: initialize — shop handed to handler unverified via body byte variance

## Question
Starting from `Request.new(raw_body:, headers:)`, called by the app's public webhook endpoint on every inbound POST, can an unprivileged attacker supply a raw body whose bytes differ from what the framework hands to `JSON.parse` (encoding conversion, BOM, trailing newline, rewound stream) so that `WebhookMetadata#shop` is the raw header value and is what the host app uses to decide whose records to touch? Determine whether SIGNATURE COVERAGE: every value acted on downstream is inside the string handed to `HmacValidator` via `to_signable_string` still holds through `Webhooks::Request#initialize`, and whether the result reaches Critical - authentication bypass: a forged or unsigned request is accepted as authentic by the app.

## Target
- File/function: `lib/shopify_api/webhooks/request.rb` -> `Webhooks::Request#initialize`
- Entrypoint: `Request.new(raw_body:, headers:)`, called by the app's public webhook endpoint on every inbound POST
- Attacker controls: a raw body whose bytes differ from what the framework hands to `JSON.parse` (encoding conversion, BOM, trailing newline, rewound stream)
- Exploit idea: `WebhookMetadata#shop` is the raw header value and is what the host app uses to decide whose records to touch
- Invariant to test: SIGNATURE COVERAGE: every value acted on downstream is inside the string handed to `HmacValidator` via `to_signable_string`
- Expected Immunefi impact: Critical - authentication bypass: a forged or unsigned request is accepted as authentic by the app (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest: sign one body with the test secret, POST it twice with different `x-shopify-shop-domain` values, assert the handler receives two different shops for one signature
