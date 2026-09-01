# Q1561: request_url — mutable shared header hash via error body content

## Question
Can an unprivileged attacker reach `Clients::HttpClient#request_url` through the protected `request_url`, a bare `"#{@base_uri_and_path}/#{request.path}"` interpolation while supplying a response body whose `errors`/`error_description` fields are echoed into the raised exception message, so that `headers = @headers` aliases the instance hash, so per-request mutations persist across requests on the same client, breaking the requirement that SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host, and ending in High - SSRF: an authenticated request carrying the app's credentials is driven to an unintended host?

## Target
- File/function: `lib/shopify_api/clients/http_client.rb` -> `Clients::HttpClient#request_url`
- Entrypoint: the protected `request_url`, a bare `"#{@base_uri_and_path}/#{request.path}"` interpolation
- Attacker controls: a response body whose `errors`/`error_description` fields are echoed into the raised exception message
- Exploit idea: `headers = @headers` aliases the instance hash, so per-request mutations persist across requests on the same client
- Invariant to test: SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host
- Expected Immunefi impact: High - SSRF: an authenticated request carrying the app's credentials is driven to an unintended host (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `X-Shopify-Access-Token` appears in no recorded request whose host is outside `TRUSTED_SHOPIFY_DOMAINS`
