# Q3081: request_url — attacker-steered retry loop via session.shop

## Question
Starting from the protected `request_url`, a bare `"#{@base_uri_and_path}/#{request.path}"` interpolation, can an unprivileged attacker supply `session.shop`, which for several flows was never passed through `ShopValidator` so that response headers decide how long and how often the authenticated request is repeated? Determine whether SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host still holds through `Clients::HttpClient#request_url`, and whether the result reaches High - SSRF: an authenticated request carrying the app's credentials is driven to an unintended host.

## Target
- File/function: `lib/shopify_api/clients/http_client.rb` -> `Clients::HttpClient#request_url`
- Entrypoint: the protected `request_url`, a bare `"#{@base_uri_and_path}/#{request.path}"` interpolation
- Attacker controls: `session.shop`, which for several flows was never passed through `ShopValidator`
- Exploit idea: response headers decide how long and how often the authenticated request is repeated
- Invariant to test: SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host
- Expected Immunefi impact: High - SSRF: an authenticated request carrying the app's credentials is driven to an unintended host (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `X-Shopify-Access-Token` appears in no recorded request whose host is outside `TRUSTED_SHOPIFY_DOMAINS`
