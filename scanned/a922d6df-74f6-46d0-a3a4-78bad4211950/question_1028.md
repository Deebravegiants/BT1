# Q1028: proxy_query — caller document executed verbatim via content-type selection

## Question
Is there a reachable state in which an unprivileged attacker, controlling the `content-type` header, which after `normalize_headers` selects between the `application/graphql` and `application/json` branches at `ShopifyAPI::Utils::GraphqlProxy.proxy_query(session:, headers:, body:, cookies:, tries:)`, wired by apps to a browser-reachable proxy route, makes `GraphqlProxy.proxy_query` return a result the caller treats as authenticated, given that the document reaches `Clients::Graphql::Admin#query` unchanged, with the merchant's access token attached? Test SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source and quantify Critical - cross-tenant access: one shop's request reads or mutates another merchant's data.

## Target
- File/function: `lib/shopify_api/utils/graphql_proxy.rb` -> `GraphqlProxy.proxy_query`
- Entrypoint: `ShopifyAPI::Utils::GraphqlProxy.proxy_query(session:, headers:, body:, cookies:, tries:)`, wired by apps to a browser-reachable proxy route
- Attacker controls: the `content-type` header, which after `normalize_headers` selects between the `application/graphql` and `application/json` branches
- Exploit idea: the document reaches `Clients::Graphql::Admin#query` unchanged, with the merchant's access token attached
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: Critical - cross-tenant access: one shop's request reads or mutates another merchant's data (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: send `Content-Type: application/json; charset=utf-8` and assert the behaviour matches the bare `application/json` case
