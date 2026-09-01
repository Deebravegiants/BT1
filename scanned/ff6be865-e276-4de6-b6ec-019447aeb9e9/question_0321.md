# Q321: proxy_query — caller document executed verbatim via header-name aliasing

## Question
Is there a reachable state in which an unprivileged attacker, controlling header names that collide after `downcase.sub("http_","").gsub("_","-")`, e.g. `HTTP_CONTENT_TYPE` and `Content_Type` at `ShopifyAPI::Utils::GraphqlProxy.proxy_query(session:, headers:, body:, cookies:, tries:)`, wired by apps to a browser-reachable proxy route, makes `GraphqlProxy.proxy_query` return a result the caller treats as authenticated, given that the document reaches `Clients::Graphql::Admin#query` unchanged, with the merchant's access token attached? Test AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right and quantify High - scope or expiry check bypass granting an operation the session was never authorized for.

## Target
- File/function: `lib/shopify_api/utils/graphql_proxy.rb` -> `GraphqlProxy.proxy_query`
- Entrypoint: `ShopifyAPI::Utils::GraphqlProxy.proxy_query(session:, headers:, body:, cookies:, tries:)`, wired by apps to a browser-reachable proxy route
- Attacker controls: header names that collide after `downcase.sub("http_","").gsub("_","-")`, e.g. `HTTP_CONTENT_TYPE` and `Content_Type`
- Exploit idea: the document reaches `Clients::Graphql::Admin#query` unchanged, with the merchant's access token attached
- Invariant to test: AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right
- Expected Immunefi impact: High - scope or expiry check bypass granting an operation the session was never authorized for (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest + WebMock: post a mutation document through `proxy_query` and assert the recorded upstream request carried the merchant's token
