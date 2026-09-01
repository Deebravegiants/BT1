# Q12: proxy_query — single gate via header-name aliasing

## Question
Trace `GraphqlProxy.proxy_query` from `ShopifyAPI::Utils::GraphqlProxy.proxy_query(session:, headers:, body:, cookies:, tries:)`, wired by apps to a browser-reachable proxy route with header names that collide after `downcase.sub("http_","").gsub("_","-")`, e.g. `HTTP_CONTENT_TYPE` and `Content_Type`: because `session.online?` is the only authorisation check; no scope, no operation allow-list, no read/write distinction, does the value that was verified stop being the value that is used? Prove the break against AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right and map it to Critical - cross-tenant access: one shop's request reads or mutates another merchant's data.

## Target
- File/function: `lib/shopify_api/utils/graphql_proxy.rb` -> `GraphqlProxy.proxy_query`
- Entrypoint: `ShopifyAPI::Utils::GraphqlProxy.proxy_query(session:, headers:, body:, cookies:, tries:)`, wired by apps to a browser-reachable proxy route
- Attacker controls: header names that collide after `downcase.sub("http_","").gsub("_","-")`, e.g. `HTTP_CONTENT_TYPE` and `Content_Type`
- Exploit idea: `session.online?` is the only authorisation check; no scope, no operation allow-list, no read/write distinction
- Invariant to test: AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right
- Expected Immunefi impact: Critical - cross-tenant access: one shop's request reads or mutates another merchant's data (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest + WebMock: post a mutation document through `proxy_query` and assert the recorded upstream request carried the merchant's token
