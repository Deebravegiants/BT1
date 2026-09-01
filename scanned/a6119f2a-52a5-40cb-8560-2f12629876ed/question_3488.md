# Q3488: request — response content into logs via response-driven retry

## Question
Does `Clients::HttpClient#request` collapse two distinct identities into one when an unprivileged attacker submits a 429 or 500 response with a chosen `retry-after` header, steering the retry loop at `HttpClient#request(request, response_as_struct:)`, the single outbound call site for every REST and GraphQL request? Show that response-controlled strings reach `Context.logger` and the exception message alongside request context, that CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted is violated, and that the consequence is High - credential or token leakage into log output or error messages.

## Target
- File/function: `lib/shopify_api/clients/http_client.rb` -> `Clients::HttpClient#request`
- Entrypoint: `HttpClient#request(request, response_as_struct:)`, the single outbound call site for every REST and GraphQL request
- Attacker controls: a 429 or 500 response with a chosen `retry-after` header, steering the retry loop
- Exploit idea: response-controlled strings reach `Context.logger` and the exception message alongside request context
- Invariant to test: CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted
- Expected Immunefi impact: High - credential or token leakage into log output or error messages (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest + WebMock: issue a request with a crafted `path` and assert the recorded request URI's host equals `session.shop`
