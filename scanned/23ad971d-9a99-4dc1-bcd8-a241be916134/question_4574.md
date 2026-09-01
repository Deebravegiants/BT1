# Q4574: append_first_party_development_headers — token attached before destination is settled via deprecation header

## Question
If an unprivileged attacker submits an `x-shopify-api-deprecated-reason` response header, which is logged verbatim to `append_first_party_development_headers`, which rewrites `Host` and `x-forwarded-host` for `.my.shop.dev`, does `Clients::HttpClient#append_first_party_development_headers` end up acting on a value that was never authenticated, because `X-Shopify-Access-Token` is added in the constructor, before any per-request check of where the URL will resolve? Close the question on SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source and on Critical - exfiltration of the app's `client_secret` and/or the OAuth authorization `code`.

## Target
- File/function: `lib/shopify_api/clients/http_client.rb` -> `Clients::HttpClient#append_first_party_development_headers`
- Entrypoint: `append_first_party_development_headers`, which rewrites `Host` and `x-forwarded-host` for `.my.shop.dev`
- Attacker controls: an `x-shopify-api-deprecated-reason` response header, which is logged verbatim
- Exploit idea: `X-Shopify-Access-Token` is added in the constructor, before any per-request check of where the URL will resolve
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: Critical - exfiltration of the app's `client_secret` and/or the OAuth authorization `code` (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: issue two requests on one `HttpClient` and assert the second does not inherit headers merged by the first
