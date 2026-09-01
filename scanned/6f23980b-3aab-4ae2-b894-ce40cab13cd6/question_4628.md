# Q4628: request — mutable shared header hash via absolute path

## Question
Starting from `HttpClient#request(request, response_as_struct:)`, the single outbound call site for every REST and GraphQL request, can an unprivileged attacker supply a `path` beginning with `/` or `//host`, which changes the authority the interpolated URL resolves to so that `headers = @headers` aliases the instance hash, so per-request mutations persist across requests on the same client? Determine whether CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted still holds through `Clients::HttpClient#request`, and whether the result reaches High - credential or token leakage into log output or error messages.

## Target
- File/function: `lib/shopify_api/clients/http_client.rb` -> `Clients::HttpClient#request`
- Entrypoint: `HttpClient#request(request, response_as_struct:)`, the single outbound call site for every REST and GraphQL request
- Attacker controls: a `path` beginning with `/` or `//host`, which changes the authority the interpolated URL resolves to
- Exploit idea: `headers = @headers` aliases the instance hash, so per-request mutations persist across requests on the same client
- Invariant to test: CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted
- Expected Immunefi impact: High - credential or token leakage into log output or error messages (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest + WebMock: issue a request with a crafted `path` and assert the recorded request URI's host equals `session.shop`
