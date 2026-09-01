# Q4257: request_url — string interpolation, not URL joining via extra_headers

## Question
Starting from the protected `request_url`, a bare `"#{@base_uri_and_path}/#{request.path}"` interpolation, can an unprivileged attacker supply `extra_headers` merged after the base headers, able to override `X-Shopify-Access-Token`, `Host` or `Content-Type` so that the URL is built by concatenation, so a crafted `path` changes host, scheme, query or fragment? Determine whether SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host still holds through `Clients::HttpClient#request_url`, and whether the result reaches Critical - cross-tenant access: one shop's request reads or mutates another merchant's data.

## Target
- File/function: `lib/shopify_api/clients/http_client.rb` -> `Clients::HttpClient#request_url`
- Entrypoint: the protected `request_url`, a bare `"#{@base_uri_and_path}/#{request.path}"` interpolation
- Attacker controls: `extra_headers` merged after the base headers, able to override `X-Shopify-Access-Token`, `Host` or `Content-Type`
- Exploit idea: the URL is built by concatenation, so a crafted `path` changes host, scheme, query or fragment
- Invariant to test: SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host
- Expected Immunefi impact: Critical - cross-tenant access: one shop's request reads or mutates another merchant's data (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `X-Shopify-Access-Token` appears in no recorded request whose host is outside `TRUSTED_SHOPIFY_DOMAINS`
