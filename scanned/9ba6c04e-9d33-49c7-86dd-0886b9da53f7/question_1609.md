# Q1609: serialized_error — dev-mode rewrite in production via api_host config

## Question
Is there a reachable state in which an unprivileged attacker, controlling an `api_host` configured so `Host` is set from `session.shop` while the connection goes elsewhere at `serialized_error`, which builds an error message from response body and headers, makes `Clients::HttpClient#serialized_error` return a result the caller treats as authenticated, given that the `DevServer` branch fires whenever the constant happens to be defined, rewriting `Host` for `.my.shop.dev`? Test SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host and quantify Critical - exfiltration of the app's `client_secret` and/or the OAuth authorization `code`.

## Target
- File/function: `lib/shopify_api/clients/http_client.rb` -> `Clients::HttpClient#serialized_error`
- Entrypoint: `serialized_error`, which builds an error message from response body and headers
- Attacker controls: an `api_host` configured so `Host` is set from `session.shop` while the connection goes elsewhere
- Exploit idea: the `DevServer` branch fires whenever the constant happens to be defined, rewriting `Host` for `.my.shop.dev`
- Invariant to test: SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host
- Expected Immunefi impact: Critical - exfiltration of the app's `client_secret` and/or the OAuth authorization `code` (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `X-Shopify-Access-Token` appears in no recorded request whose host is outside `TRUSTED_SHOPIFY_DOMAINS`
