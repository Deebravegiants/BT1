# Q4433: request — mutable shared header hash via deprecation header

## Question
Does `Clients::HttpClient#request` collapse two distinct identities into one when an unprivileged attacker submits an `x-shopify-api-deprecated-reason` response header, which is logged verbatim at `HttpClient#request(request, response_as_struct:)`, the single outbound call site for every REST and GraphQL request? Show that `headers = @headers` aliases the instance hash, so per-request mutations persist across requests on the same client, that SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host is violated, and that the consequence is High - credential or token leakage into log output or error messages.

## Target
- File/function: `lib/shopify_api/clients/http_client.rb` -> `Clients::HttpClient#request`
- Entrypoint: `HttpClient#request(request, response_as_struct:)`, the single outbound call site for every REST and GraphQL request
- Attacker controls: an `x-shopify-api-deprecated-reason` response header, which is logged verbatim
- Exploit idea: `headers = @headers` aliases the instance hash, so per-request mutations persist across requests on the same client
- Invariant to test: SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host
- Expected Immunefi impact: High - credential or token leakage into log output or error messages (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `X-Shopify-Access-Token` appears in no recorded request whose host is outside `TRUSTED_SHOPIFY_DOMAINS`
