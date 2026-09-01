# Q4013: serialized_error — attacker-steered retry loop via response-driven retry

## Question
Does `Clients::HttpClient#serialized_error` collapse two distinct identities into one when an unprivileged attacker submits a 429 or 500 response with a chosen `retry-after` header, steering the retry loop at `serialized_error`, which builds an error message from response body and headers? Show that response headers decide how long and how often the authenticated request is repeated, that SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host is violated, and that the consequence is High - credential or token leakage into log output or error messages.

## Target
- File/function: `lib/shopify_api/clients/http_client.rb` -> `Clients::HttpClient#serialized_error`
- Entrypoint: `serialized_error`, which builds an error message from response body and headers
- Attacker controls: a 429 or 500 response with a chosen `retry-after` header, steering the retry loop
- Exploit idea: response headers decide how long and how often the authenticated request is repeated
- Invariant to test: SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host
- Expected Immunefi impact: High - credential or token leakage into log output or error messages (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `X-Shopify-Access-Token` appears in no recorded request whose host is outside `TRUSTED_SHOPIFY_DOMAINS`
