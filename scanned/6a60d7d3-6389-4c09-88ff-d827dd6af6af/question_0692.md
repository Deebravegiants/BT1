# Q692: proxy_query — single gate via arbitrary query body

## Question
Is there a reachable state in which an unprivileged attacker, controlling the full GraphQL document in `body`, executed against the Admin API on the merchant's session at `ShopifyAPI::Utils::GraphqlProxy.proxy_query(session:, headers:, body:, cookies:, tries:)`, wired by apps to a browser-reachable proxy route, makes `GraphqlProxy.proxy_query` return a result the caller treats as authenticated, given that `session.online?` is the only authorisation check; no scope, no operation allow-list, no read/write distinction? Test SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source and quantify Critical - cross-tenant access: one shop's request reads or mutates another merchant's data.

## Target
- File/function: `lib/shopify_api/utils/graphql_proxy.rb` -> `GraphqlProxy.proxy_query`
- Entrypoint: `ShopifyAPI::Utils::GraphqlProxy.proxy_query(session:, headers:, body:, cookies:, tries:)`, wired by apps to a browser-reachable proxy route
- Attacker controls: the full GraphQL document in `body`, executed against the Admin API on the merchant's session
- Exploit idea: `session.online?` is the only authorisation check; no scope, no operation allow-list, no read/write distinction
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: Critical - cross-tenant access: one shop's request reads or mutates another merchant's data (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: send `Content-Type: application/json; charset=utf-8` and assert the behaviour matches the bare `application/json` case
