# Q538: proxy_query — private-app check only via tries argument

## Question
Is there a reachable state in which an unprivileged attacker, controlling the `tries:` value, repeating the authenticated upstream call at `ShopifyAPI::Utils::GraphqlProxy.proxy_query(session:, headers:, body:, cookies:, tries:)`, wired by apps to a browser-reachable proxy route, makes `GraphqlProxy.proxy_query` return a result the caller treats as authenticated, given that `Context.private?` is rejected but no per-request authorisation exists for non-private apps? Test SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host and quantify Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`).

## Target
- File/function: `lib/shopify_api/utils/graphql_proxy.rb` -> `GraphqlProxy.proxy_query`
- Entrypoint: `ShopifyAPI::Utils::GraphqlProxy.proxy_query(session:, headers:, body:, cookies:, tries:)`, wired by apps to a browser-reachable proxy route
- Attacker controls: the `tries:` value, repeating the authenticated upstream call
- Exploit idea: `Context.private?` is rejected but no per-request authorisation exists for non-private apps
- Invariant to test: SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host
- Expected Immunefi impact: Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`) (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `proxy_query` rejects a document the session's `scope` does not cover
