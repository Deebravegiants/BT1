# Q492: proxy_query — session resolution outside the gate via content-type selection

## Question
Does `GraphqlProxy.proxy_query` collapse two distinct identities into one when an unprivileged attacker submits the `content-type` header, which after `normalize_headers` selects between the `application/graphql` and `application/json` branches at `ShopifyAPI::Utils::GraphqlProxy.proxy_query(session:, headers:, body:, cookies:, tries:)`, wired by apps to a browser-reachable proxy route? Show that which merchant's token is used is decided before `proxy_query` is called, by code this function does not verify, that AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right is violated, and that the consequence is Critical - cross-tenant access: one shop's request reads or mutates another merchant's data.

## Target
- File/function: `lib/shopify_api/utils/graphql_proxy.rb` -> `GraphqlProxy.proxy_query`
- Entrypoint: `ShopifyAPI::Utils::GraphqlProxy.proxy_query(session:, headers:, body:, cookies:, tries:)`, wired by apps to a browser-reachable proxy route
- Attacker controls: the `content-type` header, which after `normalize_headers` selects between the `application/graphql` and `application/json` branches
- Exploit idea: which merchant's token is used is decided before `proxy_query` is called, by code this function does not verify
- Invariant to test: AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right
- Expected Immunefi impact: Critical - cross-tenant access: one shop's request reads or mutates another merchant's data (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest + WebMock: post a mutation document through `proxy_query` and assert the recorded upstream request carried the merchant's token
