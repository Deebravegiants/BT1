# Q4313: append_first_party_development_headers — host header split from connection host via absolute path

## Question
Starting from `append_first_party_development_headers`, which rewrites `Host` and `x-forwarded-host` for `.my.shop.dev`, can an unprivileged attacker supply a `path` beginning with `/` or `//host`, which changes the authority the interpolated URL resolves to so that when `api_host` is set, `Host` is `session.shop` while the socket goes to `api_host`, so the two identities diverge? Determine whether SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host still holds through `Clients::HttpClient#append_first_party_development_headers`, and whether the result reaches High - credential or token leakage into log output or error messages.

## Target
- File/function: `lib/shopify_api/clients/http_client.rb` -> `Clients::HttpClient#append_first_party_development_headers`
- Entrypoint: `append_first_party_development_headers`, which rewrites `Host` and `x-forwarded-host` for `.my.shop.dev`
- Attacker controls: a `path` beginning with `/` or `//host`, which changes the authority the interpolated URL resolves to
- Exploit idea: when `api_host` is set, `Host` is `session.shop` while the socket goes to `api_host`, so the two identities diverge
- Invariant to test: SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host
- Expected Immunefi impact: High - credential or token leakage into log output or error messages (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `X-Shopify-Access-Token` appears in no recorded request whose host is outside `TRUSTED_SHOPIFY_DOMAINS`
