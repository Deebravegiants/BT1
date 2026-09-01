# Q4125: initialize — host header split from connection host via request.path

## Question
Does `Clients::HttpClient#initialize` collapse two distinct identities into one when an unprivileged attacker submits the `path` on `HttpRequest`, interpolated straight into the URL with no escaping at `HttpClient.new(base_path:, session:)`, which sets `@base_uri = "https://#{api_host || session.shop}"` and attaches `X-Shopify-Access-Token`? Show that when `api_host` is set, `Host` is `session.shop` while the socket goes to `api_host`, so the two identities diverge, that SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host is violated, and that the consequence is Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`).

## Target
- File/function: `lib/shopify_api/clients/http_client.rb` -> `Clients::HttpClient#initialize`
- Entrypoint: `HttpClient.new(base_path:, session:)`, which sets `@base_uri = "https://#{api_host || session.shop}"` and attaches `X-Shopify-Access-Token`
- Attacker controls: the `path` on `HttpRequest`, interpolated straight into the URL with no escaping
- Exploit idea: when `api_host` is set, `Host` is `session.shop` while the socket goes to `api_host`, so the two identities diverge
- Invariant to test: SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host
- Expected Immunefi impact: Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`) (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `X-Shopify-Access-Token` appears in no recorded request whose host is outside `TRUSTED_SHOPIFY_DOMAINS`
