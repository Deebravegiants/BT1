# Q5496: request_url — attacker-steered retry loop via error body content

## Question
Starting from the protected `request_url`, a bare `"#{@base_uri_and_path}/#{request.path}"` interpolation, can an unprivileged attacker supply a response body whose `errors`/`error_description` fields are echoed into the raised exception message so that response headers decide how long and how often the authenticated request is repeated? Determine whether CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted still holds through `Clients::HttpClient#request_url`, and whether the result reaches High - SSRF: an authenticated request carrying the app's credentials is driven to an unintended host.

## Target
- File/function: `lib/shopify_api/clients/http_client.rb` -> `Clients::HttpClient#request_url`
- Entrypoint: the protected `request_url`, a bare `"#{@base_uri_and_path}/#{request.path}"` interpolation
- Attacker controls: a response body whose `errors`/`error_description` fields are echoed into the raised exception message
- Exploit idea: response headers decide how long and how often the authenticated request is repeated
- Invariant to test: CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted
- Expected Immunefi impact: High - SSRF: an authenticated request carrying the app's credentials is driven to an unintended host (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest + WebMock: issue a request with a crafted `path` and assert the recorded request URI's host equals `session.shop`
