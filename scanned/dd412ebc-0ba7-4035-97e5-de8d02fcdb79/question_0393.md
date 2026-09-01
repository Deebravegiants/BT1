# Q393: request — token attached before destination is settled via path traversal segments

## Question
Starting from `HttpClient#request(request, response_as_struct:)`, the single outbound call site for every REST and GraphQL request, can an unprivileged attacker supply `../` or `%2e%2e%2f` segments in `path` that climb out of the versioned base path so that `X-Shopify-Access-Token` is added in the constructor, before any per-request check of where the URL will resolve? Determine whether SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host still holds through `Clients::HttpClient#request`, and whether the result reaches High - credential or token leakage into log output or error messages.

## Target
- File/function: `lib/shopify_api/clients/http_client.rb` -> `Clients::HttpClient#request`
- Entrypoint: `HttpClient#request(request, response_as_struct:)`, the single outbound call site for every REST and GraphQL request
- Attacker controls: `../` or `%2e%2e%2f` segments in `path` that climb out of the versioned base path
- Exploit idea: `X-Shopify-Access-Token` is added in the constructor, before any per-request check of where the URL will resolve
- Invariant to test: SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host
- Expected Immunefi impact: High - credential or token leakage into log output or error messages (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `X-Shopify-Access-Token` appears in no recorded request whose host is outside `TRUSTED_SHOPIFY_DOMAINS`
