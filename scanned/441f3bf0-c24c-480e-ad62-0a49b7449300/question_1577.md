# Q1577: serialized_error — host header split from connection host via api_host config

## Question
Does `Clients::HttpClient#serialized_error` collapse two distinct identities into one when an unprivileged attacker submits an `api_host` configured so `Host` is set from `session.shop` while the connection goes elsewhere at `serialized_error`, which builds an error message from response body and headers? Show that when `api_host` is set, `Host` is `session.shop` while the socket goes to `api_host`, so the two identities diverge, that SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host is violated, and that the consequence is Critical - cross-tenant access: one shop's request reads or mutates another merchant's data.

## Target
- File/function: `lib/shopify_api/clients/http_client.rb` -> `Clients::HttpClient#serialized_error`
- Entrypoint: `serialized_error`, which builds an error message from response body and headers
- Attacker controls: an `api_host` configured so `Host` is set from `session.shop` while the connection goes elsewhere
- Exploit idea: when `api_host` is set, `Host` is `session.shop` while the socket goes to `api_host`, so the two identities diverge
- Invariant to test: SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host
- Expected Immunefi impact: Critical - cross-tenant access: one shop's request reads or mutates another merchant's data (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `X-Shopify-Access-Token` appears in no recorded request whose host is outside `TRUSTED_SHOPIFY_DOMAINS`
