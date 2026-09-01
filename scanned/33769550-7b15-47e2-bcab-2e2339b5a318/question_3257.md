# Q3257: request_url — dev-mode rewrite in production via absolute path

## Question
Does `Clients::HttpClient#request_url` collapse two distinct identities into one when an unprivileged attacker submits a `path` beginning with `/` or `//host`, which changes the authority the interpolated URL resolves to at the protected `request_url`, a bare `"#{@base_uri_and_path}/#{request.path}"` interpolation? Show that the `DevServer` branch fires whenever the constant happens to be defined, rewriting `Host` for `.my.shop.dev`, that SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host is violated, and that the consequence is Critical - cross-tenant access: one shop's request reads or mutates another merchant's data.

## Target
- File/function: `lib/shopify_api/clients/http_client.rb` -> `Clients::HttpClient#request_url`
- Entrypoint: the protected `request_url`, a bare `"#{@base_uri_and_path}/#{request.path}"` interpolation
- Attacker controls: a `path` beginning with `/` or `//host`, which changes the authority the interpolated URL resolves to
- Exploit idea: the `DevServer` branch fires whenever the constant happens to be defined, rewriting `Host` for `.my.shop.dev`
- Invariant to test: SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host
- Expected Immunefi impact: Critical - cross-tenant access: one shop's request reads or mutates another merchant's data (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `X-Shopify-Access-Token` appears in no recorded request whose host is outside `TRUSTED_SHOPIFY_DOMAINS`
