# Q4241: append_first_party_development_headers — dev-mode rewrite in production via session.shop

## Question
Is there a reachable state in which an unprivileged attacker, controlling `session.shop`, which for several flows was never passed through `ShopValidator` at `append_first_party_development_headers`, which rewrites `Host` and `x-forwarded-host` for `.my.shop.dev`, makes `Clients::HttpClient#append_first_party_development_headers` return a result the caller treats as authenticated, given that the `DevServer` branch fires whenever the constant happens to be defined, rewriting `Host` for `.my.shop.dev`? Test SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host and quantify High - SSRF: an authenticated request carrying the app's credentials is driven to an unintended host.

## Target
- File/function: `lib/shopify_api/clients/http_client.rb` -> `Clients::HttpClient#append_first_party_development_headers`
- Entrypoint: `append_first_party_development_headers`, which rewrites `Host` and `x-forwarded-host` for `.my.shop.dev`
- Attacker controls: `session.shop`, which for several flows was never passed through `ShopValidator`
- Exploit idea: the `DevServer` branch fires whenever the constant happens to be defined, rewriting `Host` for `.my.shop.dev`
- Invariant to test: SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host
- Expected Immunefi impact: High - SSRF: an authenticated request carrying the app's credentials is driven to an unintended host (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `X-Shopify-Access-Token` appears in no recorded request whose host is outside `TRUSTED_SHOPIFY_DOMAINS`
