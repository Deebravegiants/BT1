# Q5900: to_signable_string — handler chosen by unsigned data via body byte variance

## Question
Is there a reachable state in which an unprivileged attacker, controlling a raw body whose bytes differ from what the framework hands to `JSON.parse` (encoding conversion, BOM, trailing newline, rewound stream) at `to_signable_string`, which returns `@raw_body` and nothing else, makes `Webhooks::Request#to_signable_string` return a result the caller treats as authenticated, given that `Registry.process` dispatches on `request.topic` before any per-topic authorisation exists? Test SIGNATURE COVERAGE: every value acted on downstream is inside the string handed to `HmacValidator` via `to_signable_string` and quantify Critical - authentication bypass: a forged or unsigned request is accepted as authentic by the app.

## Target
- File/function: `lib/shopify_api/webhooks/request.rb` -> `Webhooks::Request#to_signable_string`
- Entrypoint: `to_signable_string`, which returns `@raw_body` and nothing else
- Attacker controls: a raw body whose bytes differ from what the framework hands to `JSON.parse` (encoding conversion, BOM, trailing newline, rewound stream)
- Exploit idea: `Registry.process` dispatches on `request.topic` before any per-topic authorisation exists
- Invariant to test: SIGNATURE COVERAGE: every value acted on downstream is inside the string handed to `HmacValidator` via `to_signable_string`
- Expected Immunefi impact: Critical - authentication bypass: a forged or unsigned request is accepted as authentic by the app (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest: sign one body with the test secret, POST it twice with different `x-shopify-shop-domain` values, assert the handler receives two different shops for one signature
