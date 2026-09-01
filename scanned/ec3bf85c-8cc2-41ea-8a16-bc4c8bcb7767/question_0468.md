# Q468: proxy_query — content-type equality via content-type selection

## Question
Is there a reachable state in which an unprivileged attacker, controlling the `content-type` header, which after `normalize_headers` selects between the `application/graphql` and `application/json` branches at `ShopifyAPI::Utils::GraphqlProxy.proxy_query(session:, headers:, body:, cookies:, tries:)`, wired by apps to a browser-reachable proxy route, makes `GraphqlProxy.proxy_query` return a result the caller treats as authenticated, given that the branch is chosen by exact string equality on a normalised header, so a parameterised or aliased header changes behaviour? Test AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right and quantify Critical - cross-tenant access: one shop's request reads or mutates another merchant's data.

## Target
- File/function: `lib/shopify_api/utils/graphql_proxy.rb` -> `GraphqlProxy.proxy_query`
- Entrypoint: `ShopifyAPI::Utils::GraphqlProxy.proxy_query(session:, headers:, body:, cookies:, tries:)`, wired by apps to a browser-reachable proxy route
- Attacker controls: the `content-type` header, which after `normalize_headers` selects between the `application/graphql` and `application/json` branches
- Exploit idea: the branch is chosen by exact string equality on a normalised header, so a parameterised or aliased header changes behaviour
- Invariant to test: AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right
- Expected Immunefi impact: Critical - cross-tenant access: one shop's request reads or mutates another merchant's data (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest + WebMock: post a mutation document through `proxy_query` and assert the recorded upstream request carried the merchant's token
