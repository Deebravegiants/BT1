# Q2001: initialize — mutable shared header hash via empty access token

## Question
Is there a reachable state in which an unprivileged attacker, controlling a session whose `access_token` is empty or whitespace, so the `X-Shopify-Access-Token` header is skipped and an unauthenticated request is issued that still returns a 200-shaped response at `HttpClient.new(base_path:, session:)`, which sets `@base_uri = "https://#{api_host || session.shop}"` and attaches `X-Shopify-Access-Token`, makes `Clients::HttpClient#initialize` return a result the caller treats as authenticated, given that `headers = @headers` aliases the instance hash, so per-request mutations persist across requests on the same client? Test SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host and quantify High - SSRF: an authenticated request carrying the app's credentials is driven to an unintended host.

## Target
- File/function: `lib/shopify_api/clients/http_client.rb` -> `Clients::HttpClient#initialize`
- Entrypoint: `HttpClient.new(base_path:, session:)`, which sets `@base_uri = "https://#{api_host || session.shop}"` and attaches `X-Shopify-Access-Token`
- Attacker controls: a session whose `access_token` is empty or whitespace, so the `X-Shopify-Access-Token` header is skipped and an unauthenticated request is issued that still returns a 200-shaped response
- Exploit idea: `headers = @headers` aliases the instance hash, so per-request mutations persist across requests on the same client
- Invariant to test: SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host
- Expected Immunefi impact: High - SSRF: an authenticated request carrying the app's credentials is driven to an unintended host (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `X-Shopify-Access-Token` appears in no recorded request whose host is outside `TRUSTED_SHOPIFY_DOMAINS`
