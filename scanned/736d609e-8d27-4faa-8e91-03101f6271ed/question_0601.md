# Q601: request — response content into logs via error body content

## Question
Is there a reachable state in which an unprivileged attacker, controlling a response body whose `errors`/`error_description` fields are echoed into the raised exception message at `HttpClient#request(request, response_as_struct:)`, the single outbound call site for every REST and GraphQL request, makes `Clients::HttpClient#request` return a result the caller treats as authenticated, given that response-controlled strings reach `Context.logger` and the exception message alongside request context? Test SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host and quantify High - SSRF: an authenticated request carrying the app's credentials is driven to an unintended host.

## Target
- File/function: `lib/shopify_api/clients/http_client.rb` -> `Clients::HttpClient#request`
- Entrypoint: `HttpClient#request(request, response_as_struct:)`, the single outbound call site for every REST and GraphQL request
- Attacker controls: a response body whose `errors`/`error_description` fields are echoed into the raised exception message
- Exploit idea: response-controlled strings reach `Context.logger` and the exception message alongside request context
- Invariant to test: SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host
- Expected Immunefi impact: High - SSRF: an authenticated request carrying the app's credentials is driven to an unintended host (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `X-Shopify-Access-Token` appears in no recorded request whose host is outside `TRUSTED_SHOPIFY_DOMAINS`
