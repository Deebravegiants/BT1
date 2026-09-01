# Q4852: append_first_party_development_headers — mutable shared header hash via empty access token

## Question
Starting from `append_first_party_development_headers`, which rewrites `Host` and `x-forwarded-host` for `.my.shop.dev`, can an unprivileged attacker supply a session whose `access_token` is empty or whitespace, so the `X-Shopify-Access-Token` header is skipped and an unauthenticated request is issued that still returns a 200-shaped response so that `headers = @headers` aliases the instance hash, so per-request mutations persist across requests on the same client? Determine whether CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted still holds through `Clients::HttpClient#append_first_party_development_headers`, and whether the result reaches Critical - cross-tenant access: one shop's request reads or mutates another merchant's data.

## Target
- File/function: `lib/shopify_api/clients/http_client.rb` -> `Clients::HttpClient#append_first_party_development_headers`
- Entrypoint: `append_first_party_development_headers`, which rewrites `Host` and `x-forwarded-host` for `.my.shop.dev`
- Attacker controls: a session whose `access_token` is empty or whitespace, so the `X-Shopify-Access-Token` header is skipped and an unauthenticated request is issued that still returns a 200-shaped response
- Exploit idea: `headers = @headers` aliases the instance hash, so per-request mutations persist across requests on the same client
- Invariant to test: CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted
- Expected Immunefi impact: Critical - cross-tenant access: one shop's request reads or mutates another merchant's data (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest + WebMock: issue a request with a crafted `path` and assert the recorded request URI's host equals `session.shop`
