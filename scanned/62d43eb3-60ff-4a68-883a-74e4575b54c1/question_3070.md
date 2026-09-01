# Q3070: append_first_party_development_headers — header override ordering via session.shop

## Question
Can `session.shop`, which for several flows was never passed through `ShopValidator`, supplied by an unprivileged attacker at `append_first_party_development_headers`, which rewrites `Host` and `x-forwarded-host` for `.my.shop.dev`, make `Clients::HttpClient#append_first_party_development_headers` and the code consuming its result disagree, given that `extra_headers` is merged last, so a caller-influenced header wins over the security-relevant defaults? The binding to test is SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source; the impact to prove is Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`).

## Target
- File/function: `lib/shopify_api/clients/http_client.rb` -> `Clients::HttpClient#append_first_party_development_headers`
- Entrypoint: `append_first_party_development_headers`, which rewrites `Host` and `x-forwarded-host` for `.my.shop.dev`
- Attacker controls: `session.shop`, which for several flows was never passed through `ShopValidator`
- Exploit idea: `extra_headers` is merged last, so a caller-influenced header wins over the security-relevant defaults
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`) (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: issue two requests on one `HttpClient` and assert the second does not inherit headers merged by the first
