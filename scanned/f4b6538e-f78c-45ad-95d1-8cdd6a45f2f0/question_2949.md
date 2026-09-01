# Q2949: request — host header split from connection host via path traversal segments

## Question
Does `Clients::HttpClient#request` collapse two distinct identities into one when an unprivileged attacker submits `../` or `%2e%2e%2f` segments in `path` that climb out of the versioned base path at `HttpClient#request(request, response_as_struct:)`, the single outbound call site for every REST and GraphQL request? Show that when `api_host` is set, `Host` is `session.shop` while the socket goes to `api_host`, so the two identities diverge, that SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host is violated, and that the consequence is Critical - exfiltration of the app's `client_secret` and/or the OAuth authorization `code`.

## Target
- File/function: `lib/shopify_api/clients/http_client.rb` -> `Clients::HttpClient#request`
- Entrypoint: `HttpClient#request(request, response_as_struct:)`, the single outbound call site for every REST and GraphQL request
- Attacker controls: `../` or `%2e%2e%2f` segments in `path` that climb out of the versioned base path
- Exploit idea: when `api_host` is set, `Host` is `session.shop` while the socket goes to `api_host`, so the two identities diverge
- Invariant to test: SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host
- Expected Immunefi impact: Critical - exfiltration of the app's `client_secret` and/or the OAuth authorization `code` (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `X-Shopify-Access-Token` appears in no recorded request whose host is outside `TRUSTED_SHOPIFY_DOMAINS`
