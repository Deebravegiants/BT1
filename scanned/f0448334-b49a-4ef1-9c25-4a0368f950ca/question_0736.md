# Q736: proxy_query — caller document executed verbatim via arbitrary query body

## Question
Starting from `ShopifyAPI::Utils::GraphqlProxy.proxy_query(session:, headers:, body:, cookies:, tries:)`, wired by apps to a browser-reachable proxy route, can an unprivileged attacker supply the full GraphQL document in `body`, executed against the Admin API on the merchant's session so that the document reaches `Clients::Graphql::Admin#query` unchanged, with the merchant's access token attached? Determine whether SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host still holds through `GraphqlProxy.proxy_query`, and whether the result reaches Critical - cross-tenant access: one shop's request reads or mutates another merchant's data.

## Target
- File/function: `lib/shopify_api/utils/graphql_proxy.rb` -> `GraphqlProxy.proxy_query`
- Entrypoint: `ShopifyAPI::Utils::GraphqlProxy.proxy_query(session:, headers:, body:, cookies:, tries:)`, wired by apps to a browser-reachable proxy route
- Attacker controls: the full GraphQL document in `body`, executed against the Admin API on the merchant's session
- Exploit idea: the document reaches `Clients::Graphql::Admin#query` unchanged, with the merchant's access token attached
- Invariant to test: SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host
- Expected Immunefi impact: Critical - cross-tenant access: one shop's request reads or mutates another merchant's data (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `proxy_query` rejects a document the session's `scope` does not cover
