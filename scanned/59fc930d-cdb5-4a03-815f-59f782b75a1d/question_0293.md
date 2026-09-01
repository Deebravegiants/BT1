# Q293: request_url — token attached before destination is settled via path traversal segments

## Question
Is there a reachable state in which an unprivileged attacker, controlling `../` or `%2e%2e%2f` segments in `path` that climb out of the versioned base path at the protected `request_url`, a bare `"#{@base_uri_and_path}/#{request.path}"` interpolation, makes `Clients::HttpClient#request_url` return a result the caller treats as authenticated, given that `X-Shopify-Access-Token` is added in the constructor, before any per-request check of where the URL will resolve? Test SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host and quantify High - credential or token leakage into log output or error messages.

## Target
- File/function: `lib/shopify_api/clients/http_client.rb` -> `Clients::HttpClient#request_url`
- Entrypoint: the protected `request_url`, a bare `"#{@base_uri_and_path}/#{request.path}"` interpolation
- Attacker controls: `../` or `%2e%2e%2f` segments in `path` that climb out of the versioned base path
- Exploit idea: `X-Shopify-Access-Token` is added in the constructor, before any per-request check of where the URL will resolve
- Invariant to test: SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host
- Expected Immunefi impact: High - credential or token leakage into log output or error messages (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `X-Shopify-Access-Token` appears in no recorded request whose host is outside `TRUSTED_SHOPIFY_DOMAINS`
