# Q3653: initialize — string interpolation, not URL joining via error body content

## Question
Is there a reachable state in which an unprivileged attacker, controlling a response body whose `errors`/`error_description` fields are echoed into the raised exception message at `HttpClient.new(base_path:, session:)`, which sets `@base_uri = "https://#{api_host || session.shop}"` and attaches `X-Shopify-Access-Token`, makes `Clients::HttpClient#initialize` return a result the caller treats as authenticated, given that the URL is built by concatenation, so a crafted `path` changes host, scheme, query or fragment? Test SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host and quantify High - credential or token leakage into log output or error messages.

## Target
- File/function: `lib/shopify_api/clients/http_client.rb` -> `Clients::HttpClient#initialize`
- Entrypoint: `HttpClient.new(base_path:, session:)`, which sets `@base_uri = "https://#{api_host || session.shop}"` and attaches `X-Shopify-Access-Token`
- Attacker controls: a response body whose `errors`/`error_description` fields are echoed into the raised exception message
- Exploit idea: the URL is built by concatenation, so a crafted `path` changes host, scheme, query or fragment
- Invariant to test: SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host
- Expected Immunefi impact: High - credential or token leakage into log output or error messages (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `X-Shopify-Access-Token` appears in no recorded request whose host is outside `TRUSTED_SHOPIFY_DOMAINS`
