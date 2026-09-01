# Q2181: request_url — response content into logs via response-driven retry

## Question
Can a 429 or 500 response with a chosen `retry-after` header, steering the retry loop, supplied by an unprivileged attacker at the protected `request_url`, a bare `"#{@base_uri_and_path}/#{request.path}"` interpolation, make `Clients::HttpClient#request_url` and the code consuming its result disagree, given that response-controlled strings reach `Context.logger` and the exception message alongside request context? The binding to test is SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host; the impact to prove is High - SSRF: an authenticated request carrying the app's credentials is driven to an unintended host.

## Target
- File/function: `lib/shopify_api/clients/http_client.rb` -> `Clients::HttpClient#request_url`
- Entrypoint: the protected `request_url`, a bare `"#{@base_uri_and_path}/#{request.path}"` interpolation
- Attacker controls: a 429 or 500 response with a chosen `retry-after` header, steering the retry loop
- Exploit idea: response-controlled strings reach `Context.logger` and the exception message alongside request context
- Invariant to test: SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host
- Expected Immunefi impact: High - SSRF: an authenticated request carrying the app's credentials is driven to an unintended host (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `X-Shopify-Access-Token` appears in no recorded request whose host is outside `TRUSTED_SHOPIFY_DOMAINS`
