# Q1625: serialized_error — dev-mode rewrite in production via path traversal segments

## Question
Starting from `serialized_error`, which builds an error message from response body and headers, can an unprivileged attacker supply `../` or `%2e%2e%2f` segments in `path` that climb out of the versioned base path so that the `DevServer` branch fires whenever the constant happens to be defined, rewriting `Host` for `.my.shop.dev`? Determine whether SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host still holds through `Clients::HttpClient#serialized_error`, and whether the result reaches Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`).

## Target
- File/function: `lib/shopify_api/clients/http_client.rb` -> `Clients::HttpClient#serialized_error`
- Entrypoint: `serialized_error`, which builds an error message from response body and headers
- Attacker controls: `../` or `%2e%2e%2f` segments in `path` that climb out of the versioned base path
- Exploit idea: the `DevServer` branch fires whenever the constant happens to be defined, rewriting `Host` for `.my.shop.dev`
- Invariant to test: SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host
- Expected Immunefi impact: Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`) (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `X-Shopify-Access-Token` appears in no recorded request whose host is outside `TRUSTED_SHOPIFY_DOMAINS`
