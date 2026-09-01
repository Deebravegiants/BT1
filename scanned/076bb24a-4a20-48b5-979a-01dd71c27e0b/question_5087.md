# Q5087: request_url — token attached before destination is settled via extra_headers

## Question
Trace `Clients::HttpClient#request_url` from the protected `request_url`, a bare `"#{@base_uri_and_path}/#{request.path}"` interpolation with `extra_headers` merged after the base headers, able to override `X-Shopify-Access-Token`, `Host` or `Content-Type`: because `X-Shopify-Access-Token` is added in the constructor, before any per-request check of where the URL will resolve, does the value that was verified stop being the value that is used? Prove the break against AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right and map it to Critical - cross-tenant access: one shop's request reads or mutates another merchant's data.

## Target
- File/function: `lib/shopify_api/clients/http_client.rb` -> `Clients::HttpClient#request_url`
- Entrypoint: the protected `request_url`, a bare `"#{@base_uri_and_path}/#{request.path}"` interpolation
- Attacker controls: `extra_headers` merged after the base headers, able to override `X-Shopify-Access-Token`, `Host` or `Content-Type`
- Exploit idea: `X-Shopify-Access-Token` is added in the constructor, before any per-request check of where the URL will resolve
- Invariant to test: AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right
- Expected Immunefi impact: Critical - cross-tenant access: one shop's request reads or mutates another merchant's data (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert the raised `HttpResponseError` message contains no access token, `client_secret` or `Authorization` value
