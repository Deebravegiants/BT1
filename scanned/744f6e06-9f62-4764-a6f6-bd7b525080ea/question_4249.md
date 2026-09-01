# Q4249: serialized_error — token attached before destination is settled via absolute path

## Question
Can an unprivileged attacker reach `Clients::HttpClient#serialized_error` through `serialized_error`, which builds an error message from response body and headers while supplying a `path` beginning with `/` or `//host`, which changes the authority the interpolated URL resolves to, so that `X-Shopify-Access-Token` is added in the constructor, before any per-request check of where the URL will resolve, breaking the requirement that SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host, and ending in Critical - exfiltration of the app's `client_secret` and/or the OAuth authorization `code`?

## Target
- File/function: `lib/shopify_api/clients/http_client.rb` -> `Clients::HttpClient#serialized_error`
- Entrypoint: `serialized_error`, which builds an error message from response body and headers
- Attacker controls: a `path` beginning with `/` or `//host`, which changes the authority the interpolated URL resolves to
- Exploit idea: `X-Shopify-Access-Token` is added in the constructor, before any per-request check of where the URL will resolve
- Invariant to test: SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host
- Expected Immunefi impact: Critical - exfiltration of the app's `client_secret` and/or the OAuth authorization `code` (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `X-Shopify-Access-Token` appears in no recorded request whose host is outside `TRUSTED_SHOPIFY_DOMAINS`
