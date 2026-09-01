# Q3441: shopify_header — header collision via underscore/dash aliasing

## Question
Can header names that collide after `downcase.sub("http_","").gsub("_","-")`, e.g. `HTTP_X_SHOPIFY_TOPIC` vs `X-Shopify-Topic`, supplied by an unprivileged attacker at the private `shopify_header`, which prefers `shopify-<name>` over `x-shopify-<name>`, make `Webhooks::Request#shopify_header` and the code consuming its result disagree, given that two spellings of one logical header resolve differently in `initialize`'s presence check than in `shopify_header`'s lookup? The binding to test is BYTE IDENTITY: the bytes passed to `compute_signature` == the bytes later parsed and acted on; the impact to prove is Critical - cross-tenant access: one shop's request reads or mutates another merchant's data.

## Target
- File/function: `lib/shopify_api/webhooks/request.rb` -> `Webhooks::Request#shopify_header`
- Entrypoint: the private `shopify_header`, which prefers `shopify-<name>` over `x-shopify-<name>`
- Attacker controls: header names that collide after `downcase.sub("http_","").gsub("_","-")`, e.g. `HTTP_X_SHOPIFY_TOPIC` vs `X-Shopify-Topic`
- Exploit idea: two spellings of one logical header resolve differently in `initialize`'s presence check than in `shopify_header`'s lookup
- Invariant to test: BYTE IDENTITY: the bytes passed to `compute_signature` == the bytes later parsed and acted on
- Expected Immunefi impact: Critical - cross-tenant access: one shop's request reads or mutates another merchant's data (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `Request#hmac` yields the same value for two different header strings, then assert `HmacValidator.validate` accepts both
