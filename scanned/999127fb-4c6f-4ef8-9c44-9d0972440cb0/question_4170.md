# Q4170: append_first_party_development_headers — host header split from connection host via empty access token

## Question
Trace `Clients::HttpClient#append_first_party_development_headers` from `append_first_party_development_headers`, which rewrites `Host` and `x-forwarded-host` for `.my.shop.dev` with a session whose `access_token` is empty or whitespace, so the `X-Shopify-Access-Token` header is skipped and an unauthenticated request is issued that still returns a 200-shaped response: because when `api_host` is set, `Host` is `session.shop` while the socket goes to `api_host`, so the two identities diverge, does the value that was verified stop being the value that is used? Prove the break against SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source and map it to Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`).

## Target
- File/function: `lib/shopify_api/clients/http_client.rb` -> `Clients::HttpClient#append_first_party_development_headers`
- Entrypoint: `append_first_party_development_headers`, which rewrites `Host` and `x-forwarded-host` for `.my.shop.dev`
- Attacker controls: a session whose `access_token` is empty or whitespace, so the `X-Shopify-Access-Token` header is skipped and an unauthenticated request is issued that still returns a 200-shaped response
- Exploit idea: when `api_host` is set, `Host` is `session.shop` while the socket goes to `api_host`, so the two identities diverge
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`) (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: issue two requests on one `HttpClient` and assert the second does not inherit headers merged by the first
