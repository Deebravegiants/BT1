# Q1801: append_first_party_development_headers — token attached before destination is settled via session.shop

## Question
Does `Clients::HttpClient#append_first_party_development_headers` collapse two distinct identities into one when an unprivileged attacker submits `session.shop`, which for several flows was never passed through `ShopValidator` at `append_first_party_development_headers`, which rewrites `Host` and `x-forwarded-host` for `.my.shop.dev`? Show that `X-Shopify-Access-Token` is added in the constructor, before any per-request check of where the URL will resolve, that SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host is violated, and that the consequence is High - SSRF: an authenticated request carrying the app's credentials is driven to an unintended host.

## Target
- File/function: `lib/shopify_api/clients/http_client.rb` -> `Clients::HttpClient#append_first_party_development_headers`
- Entrypoint: `append_first_party_development_headers`, which rewrites `Host` and `x-forwarded-host` for `.my.shop.dev`
- Attacker controls: `session.shop`, which for several flows was never passed through `ShopValidator`
- Exploit idea: `X-Shopify-Access-Token` is added in the constructor, before any per-request check of where the URL will resolve
- Invariant to test: SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host
- Expected Immunefi impact: High - SSRF: an authenticated request carrying the app's credentials is driven to an unintended host (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `X-Shopify-Access-Token` appears in no recorded request whose host is outside `TRUSTED_SHOPIFY_DOMAINS`
