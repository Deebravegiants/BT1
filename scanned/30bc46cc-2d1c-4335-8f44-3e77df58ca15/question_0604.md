# Q604: proxy_query — normalisation collision via content-type selection

## Question
Does `GraphqlProxy.proxy_query` collapse two distinct identities into one when an unprivileged attacker submits the `content-type` header, which after `normalize_headers` selects between the `application/graphql` and `application/json` branches at `ShopifyAPI::Utils::GraphqlProxy.proxy_query(session:, headers:, body:, cookies:, tries:)`, wired by apps to a browser-reachable proxy route? Show that two different inbound header names normalise to one key, and which value survives depends on hash ordering, that SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host is violated, and that the consequence is Critical - cross-tenant access: one shop's request reads or mutates another merchant's data.

## Target
- File/function: `lib/shopify_api/utils/graphql_proxy.rb` -> `GraphqlProxy.proxy_query`
- Entrypoint: `ShopifyAPI::Utils::GraphqlProxy.proxy_query(session:, headers:, body:, cookies:, tries:)`, wired by apps to a browser-reachable proxy route
- Attacker controls: the `content-type` header, which after `normalize_headers` selects between the `application/graphql` and `application/json` branches
- Exploit idea: two different inbound header names normalise to one key, and which value survives depends on hash ordering
- Invariant to test: SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host
- Expected Immunefi impact: Critical - cross-tenant access: one shop's request reads or mutates another merchant's data (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `proxy_query` rejects a document the session's `scope` does not cover
