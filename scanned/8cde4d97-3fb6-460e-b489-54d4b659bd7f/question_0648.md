# Q648: proxy_query — private-app check only via session supplied by the route

## Question
Can the `session:` argument, if the host app resolves it from a cookie or id token the attacker influences, supplied by an unprivileged attacker at `ShopifyAPI::Utils::GraphqlProxy.proxy_query(session:, headers:, body:, cookies:, tries:)`, wired by apps to a browser-reachable proxy route, make `GraphqlProxy.proxy_query` and the code consuming its result disagree, given that `Context.private?` is rejected but no per-request authorisation exists for non-private apps? The binding to test is AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right; the impact to prove is Critical - cross-tenant access: one shop's request reads or mutates another merchant's data.

## Target
- File/function: `lib/shopify_api/utils/graphql_proxy.rb` -> `GraphqlProxy.proxy_query`
- Entrypoint: `ShopifyAPI::Utils::GraphqlProxy.proxy_query(session:, headers:, body:, cookies:, tries:)`, wired by apps to a browser-reachable proxy route
- Attacker controls: the `session:` argument, if the host app resolves it from a cookie or id token the attacker influences
- Exploit idea: `Context.private?` is rejected but no per-request authorisation exists for non-private apps
- Invariant to test: AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right
- Expected Immunefi impact: Critical - cross-tenant access: one shop's request reads or mutates another merchant's data (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest + WebMock: post a mutation document through `proxy_query` and assert the recorded upstream request carried the merchant's token
