# Q906: proxy_query — single gate via content-type selection

## Question
If an unprivileged attacker submits the `content-type` header, which after `normalize_headers` selects between the `application/graphql` and `application/json` branches to `ShopifyAPI::Utils::GraphqlProxy.proxy_query(session:, headers:, body:, cookies:, tries:)`, wired by apps to a browser-reachable proxy route, does `GraphqlProxy.proxy_query` end up acting on a value that was never authenticated, because `session.online?` is the only authorisation check; no scope, no operation allow-list, no read/write distinction? Close the question on AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right and on Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`).

## Target
- File/function: `lib/shopify_api/utils/graphql_proxy.rb` -> `GraphqlProxy.proxy_query`
- Entrypoint: `ShopifyAPI::Utils::GraphqlProxy.proxy_query(session:, headers:, body:, cookies:, tries:)`, wired by apps to a browser-reachable proxy route
- Attacker controls: the `content-type` header, which after `normalize_headers` selects between the `application/graphql` and `application/json` branches
- Exploit idea: `session.online?` is the only authorisation check; no scope, no operation allow-list, no read/write distinction
- Invariant to test: AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right
- Expected Immunefi impact: Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`) (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest + WebMock: post a mutation document through `proxy_query` and assert the recorded upstream request carried the merchant's token
