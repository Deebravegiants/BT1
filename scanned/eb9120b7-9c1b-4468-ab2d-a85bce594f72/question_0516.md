# Q516: proxy_query — private-app check only via arbitrary query body

## Question
Trace `GraphqlProxy.proxy_query` from `ShopifyAPI::Utils::GraphqlProxy.proxy_query(session:, headers:, body:, cookies:, tries:)`, wired by apps to a browser-reachable proxy route with the full GraphQL document in `body`, executed against the Admin API on the merchant's session: because `Context.private?` is rejected but no per-request authorisation exists for non-private apps, does the value that was verified stop being the value that is used? Prove the break against AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right and map it to Critical - cross-tenant access: one shop's request reads or mutates another merchant's data.

## Target
- File/function: `lib/shopify_api/utils/graphql_proxy.rb` -> `GraphqlProxy.proxy_query`
- Entrypoint: `ShopifyAPI::Utils::GraphqlProxy.proxy_query(session:, headers:, body:, cookies:, tries:)`, wired by apps to a browser-reachable proxy route
- Attacker controls: the full GraphQL document in `body`, executed against the Admin API on the merchant's session
- Exploit idea: `Context.private?` is rejected but no per-request authorisation exists for non-private apps
- Invariant to test: AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right
- Expected Immunefi impact: Critical - cross-tenant access: one shop's request reads or mutates another merchant's data (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest + WebMock: post a mutation document through `proxy_query` and assert the recorded upstream request carried the merchant's token
