# Q3933: append_first_party_development_headers — response content into logs via base_path argument

## Question
Is there a reachable state in which an unprivileged attacker, controlling the `base_path:` argument, concatenated into `@base_uri_and_path` with no separator normalisation at `append_first_party_development_headers`, which rewrites `Host` and `x-forwarded-host` for `.my.shop.dev`, makes `Clients::HttpClient#append_first_party_development_headers` return a result the caller treats as authenticated, given that response-controlled strings reach `Context.logger` and the exception message alongside request context? Test SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host and quantify High - credential or token leakage into log output or error messages.

## Target
- File/function: `lib/shopify_api/clients/http_client.rb` -> `Clients::HttpClient#append_first_party_development_headers`
- Entrypoint: `append_first_party_development_headers`, which rewrites `Host` and `x-forwarded-host` for `.my.shop.dev`
- Attacker controls: the `base_path:` argument, concatenated into `@base_uri_and_path` with no separator normalisation
- Exploit idea: response-controlled strings reach `Context.logger` and the exception message alongside request context
- Invariant to test: SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host
- Expected Immunefi impact: High - credential or token leakage into log output or error messages (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `X-Shopify-Access-Token` appears in no recorded request whose host is outside `TRUSTED_SHOPIFY_DOMAINS`
