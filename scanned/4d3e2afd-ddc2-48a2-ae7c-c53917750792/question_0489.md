# Q489: append_first_party_development_headers — mutable shared header hash via response-driven retry

## Question
Is there a reachable state in which an unprivileged attacker, controlling a 429 or 500 response with a chosen `retry-after` header, steering the retry loop at `append_first_party_development_headers`, which rewrites `Host` and `x-forwarded-host` for `.my.shop.dev`, makes `Clients::HttpClient#append_first_party_development_headers` return a result the caller treats as authenticated, given that `headers = @headers` aliases the instance hash, so per-request mutations persist across requests on the same client? Test SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host and quantify Critical - exfiltration of the app's `client_secret` and/or the OAuth authorization `code`.

## Target
- File/function: `lib/shopify_api/clients/http_client.rb` -> `Clients::HttpClient#append_first_party_development_headers`
- Entrypoint: `append_first_party_development_headers`, which rewrites `Host` and `x-forwarded-host` for `.my.shop.dev`
- Attacker controls: a 429 or 500 response with a chosen `retry-after` header, steering the retry loop
- Exploit idea: `headers = @headers` aliases the instance hash, so per-request mutations persist across requests on the same client
- Invariant to test: SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host
- Expected Immunefi impact: Critical - exfiltration of the app's `client_secret` and/or the OAuth authorization `code` (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `X-Shopify-Access-Token` appears in no recorded request whose host is outside `TRUSTED_SHOPIFY_DOMAINS`
