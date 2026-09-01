# Q371: proxy_query — content-type equality via session supplied by the route

## Question
Can an unprivileged attacker reach `GraphqlProxy.proxy_query` through `ShopifyAPI::Utils::GraphqlProxy.proxy_query(session:, headers:, body:, cookies:, tries:)`, wired by apps to a browser-reachable proxy route while supplying the `session:` argument, if the host app resolves it from a cookie or id token the attacker influences, so that the branch is chosen by exact string equality on a normalised header, so a parameterised or aliased header changes behaviour, breaking the requirement that SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source, and ending in Critical - cross-user access inside one shop: one staff user's online session is served to another?

## Target
- File/function: `lib/shopify_api/utils/graphql_proxy.rb` -> `GraphqlProxy.proxy_query`
- Entrypoint: `ShopifyAPI::Utils::GraphqlProxy.proxy_query(session:, headers:, body:, cookies:, tries:)`, wired by apps to a browser-reachable proxy route
- Attacker controls: the `session:` argument, if the host app resolves it from a cookie or id token the attacker influences
- Exploit idea: the branch is chosen by exact string equality on a normalised header, so a parameterised or aliased header changes behaviour
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: Critical - cross-user access inside one shop: one staff user's online session is served to another (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: send `Content-Type: application/json; charset=utf-8` and assert the behaviour matches the bare `application/json` case
