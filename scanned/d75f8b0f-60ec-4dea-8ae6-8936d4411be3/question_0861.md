# Q861: serialized_error — header override ordering via shop.dev host

## Question
Can an unprivileged attacker reach `Clients::HttpClient#serialized_error` through `serialized_error`, which builds an error message from response body and headers while supplying a `session.shop` or `Host` header containing `.my.shop.dev`, entering the first-party development header rewrite, so that `extra_headers` is merged last, so a caller-influenced header wins over the security-relevant defaults, breaking the requirement that SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host, and ending in High - SSRF: an authenticated request carrying the app's credentials is driven to an unintended host?

## Target
- File/function: `lib/shopify_api/clients/http_client.rb` -> `Clients::HttpClient#serialized_error`
- Entrypoint: `serialized_error`, which builds an error message from response body and headers
- Attacker controls: a `session.shop` or `Host` header containing `.my.shop.dev`, entering the first-party development header rewrite
- Exploit idea: `extra_headers` is merged last, so a caller-influenced header wins over the security-relevant defaults
- Invariant to test: SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host
- Expected Immunefi impact: High - SSRF: an authenticated request carrying the app's credentials is driven to an unintended host (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `X-Shopify-Access-Token` appears in no recorded request whose host is outside `TRUSTED_SHOPIFY_DOMAINS`
