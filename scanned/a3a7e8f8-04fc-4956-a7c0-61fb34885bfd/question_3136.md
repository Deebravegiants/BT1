# Q3136: append_first_party_development_headers — attacker-steered retry loop via empty access token

## Question
Can an unprivileged attacker reach `Clients::HttpClient#append_first_party_development_headers` through `append_first_party_development_headers`, which rewrites `Host` and `x-forwarded-host` for `.my.shop.dev` while supplying a session whose `access_token` is empty or whitespace, so the `X-Shopify-Access-Token` header is skipped and an unauthenticated request is issued that still returns a 200-shaped response, so that response headers decide how long and how often the authenticated request is repeated, breaking the requirement that CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted, and ending in High - SSRF: an authenticated request carrying the app's credentials is driven to an unintended host?

## Target
- File/function: `lib/shopify_api/clients/http_client.rb` -> `Clients::HttpClient#append_first_party_development_headers`
- Entrypoint: `append_first_party_development_headers`, which rewrites `Host` and `x-forwarded-host` for `.my.shop.dev`
- Attacker controls: a session whose `access_token` is empty or whitespace, so the `X-Shopify-Access-Token` header is skipped and an unauthenticated request is issued that still returns a 200-shaped response
- Exploit idea: response headers decide how long and how often the authenticated request is repeated
- Invariant to test: CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted
- Expected Immunefi impact: High - SSRF: an authenticated request carrying the app's credentials is driven to an unintended host (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest + WebMock: issue a request with a crafted `path` and assert the recorded request URI's host equals `session.shop`
