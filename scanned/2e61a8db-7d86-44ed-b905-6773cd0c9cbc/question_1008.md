# Q1008: proxy_query — session resolution outside the gate via tries argument

## Question
Can an unprivileged attacker reach `GraphqlProxy.proxy_query` through `ShopifyAPI::Utils::GraphqlProxy.proxy_query(session:, headers:, body:, cookies:, tries:)`, wired by apps to a browser-reachable proxy route while supplying the `tries:` value, repeating the authenticated upstream call, so that which merchant's token is used is decided before `proxy_query` is called, by code this function does not verify, breaking the requirement that AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right, and ending in Critical - cross-tenant access: one shop's request reads or mutates another merchant's data?

## Target
- File/function: `lib/shopify_api/utils/graphql_proxy.rb` -> `GraphqlProxy.proxy_query`
- Entrypoint: `ShopifyAPI::Utils::GraphqlProxy.proxy_query(session:, headers:, body:, cookies:, tries:)`, wired by apps to a browser-reachable proxy route
- Attacker controls: the `tries:` value, repeating the authenticated upstream call
- Exploit idea: which merchant's token is used is decided before `proxy_query` is called, by code this function does not verify
- Invariant to test: AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right
- Expected Immunefi impact: Critical - cross-tenant access: one shop's request reads or mutates another merchant's data (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest + WebMock: post a mutation document through `proxy_query` and assert the recorded upstream request carried the merchant's token
