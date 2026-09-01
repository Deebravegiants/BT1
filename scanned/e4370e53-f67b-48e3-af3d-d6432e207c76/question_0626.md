# Q626: proxy_query — content-type equality via header-name aliasing

## Question
If an unprivileged attacker submits header names that collide after `downcase.sub("http_","").gsub("_","-")`, e.g. `HTTP_CONTENT_TYPE` and `Content_Type` to `ShopifyAPI::Utils::GraphqlProxy.proxy_query(session:, headers:, body:, cookies:, tries:)`, wired by apps to a browser-reachable proxy route, does `GraphqlProxy.proxy_query` end up acting on a value that was never authenticated, because the branch is chosen by exact string equality on a normalised header, so a parameterised or aliased header changes behaviour? Close the question on SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source and on Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`).

## Target
- File/function: `lib/shopify_api/utils/graphql_proxy.rb` -> `GraphqlProxy.proxy_query`
- Entrypoint: `ShopifyAPI::Utils::GraphqlProxy.proxy_query(session:, headers:, body:, cookies:, tries:)`, wired by apps to a browser-reachable proxy route
- Attacker controls: header names that collide after `downcase.sub("http_","").gsub("_","-")`, e.g. `HTTP_CONTENT_TYPE` and `Content_Type`
- Exploit idea: the branch is chosen by exact string equality on a normalised header, so a parameterised or aliased header changes behaviour
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`) (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: send `Content-Type: application/json; charset=utf-8` and assert the behaviour matches the bare `application/json` case
