# Q4977: initialize — host header split from connection host via empty access token

## Question
Can an unprivileged attacker reach `Clients::HttpClient#initialize` through `HttpClient.new(base_path:, session:)`, which sets `@base_uri = "https://#{api_host || session.shop}"` and attaches `X-Shopify-Access-Token` while supplying a session whose `access_token` is empty or whitespace, so the `X-Shopify-Access-Token` header is skipped and an unauthenticated request is issued that still returns a 200-shaped response, so that when `api_host` is set, `Host` is `session.shop` while the socket goes to `api_host`, so the two identities diverge, breaking the requirement that SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host, and ending in Critical - cross-tenant access: one shop's request reads or mutates another merchant's data?

## Target
- File/function: `lib/shopify_api/clients/http_client.rb` -> `Clients::HttpClient#initialize`
- Entrypoint: `HttpClient.new(base_path:, session:)`, which sets `@base_uri = "https://#{api_host || session.shop}"` and attaches `X-Shopify-Access-Token`
- Attacker controls: a session whose `access_token` is empty or whitespace, so the `X-Shopify-Access-Token` header is skipped and an unauthenticated request is issued that still returns a 200-shaped response
- Exploit idea: when `api_host` is set, `Host` is `session.shop` while the socket goes to `api_host`, so the two identities diverge
- Invariant to test: SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host
- Expected Immunefi impact: Critical - cross-tenant access: one shop's request reads or mutates another merchant's data (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `X-Shopify-Access-Token` appears in no recorded request whose host is outside `TRUSTED_SHOPIFY_DOMAINS`
