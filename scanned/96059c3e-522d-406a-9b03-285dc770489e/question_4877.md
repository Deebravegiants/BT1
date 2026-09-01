# Q4877: request — attacker-steered retry loop via absolute path

## Question
Trace `Clients::HttpClient#request` from `HttpClient#request(request, response_as_struct:)`, the single outbound call site for every REST and GraphQL request with a `path` beginning with `/` or `//host`, which changes the authority the interpolated URL resolves to: because response headers decide how long and how often the authenticated request is repeated, does the value that was verified stop being the value that is used? Prove the break against SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host and map it to Critical - cross-tenant access: one shop's request reads or mutates another merchant's data.

## Target
- File/function: `lib/shopify_api/clients/http_client.rb` -> `Clients::HttpClient#request`
- Entrypoint: `HttpClient#request(request, response_as_struct:)`, the single outbound call site for every REST and GraphQL request
- Attacker controls: a `path` beginning with `/` or `//host`, which changes the authority the interpolated URL resolves to
- Exploit idea: response headers decide how long and how often the authenticated request is repeated
- Invariant to test: SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host
- Expected Immunefi impact: Critical - cross-tenant access: one shop's request reads or mutates another merchant's data (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `X-Shopify-Access-Token` appears in no recorded request whose host is outside `TRUSTED_SHOPIFY_DOMAINS`
