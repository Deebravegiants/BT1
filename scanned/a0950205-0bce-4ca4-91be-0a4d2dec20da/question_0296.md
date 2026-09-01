# Q296: proxy_query — private-app check only via content-type with parameters

## Question
Does `GraphqlProxy.proxy_query` collapse two distinct identities into one when an unprivileged attacker submits a `content-type` such as `application/json; charset=utf-8`, which matches neither literal branch at `ShopifyAPI::Utils::GraphqlProxy.proxy_query(session:, headers:, body:, cookies:, tries:)`, wired by apps to a browser-reachable proxy route? Show that `Context.private?` is rejected but no per-request authorisation exists for non-private apps, that SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source is violated, and that the consequence is Critical - cross-tenant access: one shop's request reads or mutates another merchant's data.

## Target
- File/function: `lib/shopify_api/utils/graphql_proxy.rb` -> `GraphqlProxy.proxy_query`
- Entrypoint: `ShopifyAPI::Utils::GraphqlProxy.proxy_query(session:, headers:, body:, cookies:, tries:)`, wired by apps to a browser-reachable proxy route
- Attacker controls: a `content-type` such as `application/json; charset=utf-8`, which matches neither literal branch
- Exploit idea: `Context.private?` is rejected but no per-request authorisation exists for non-private apps
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: Critical - cross-tenant access: one shop's request reads or mutates another merchant's data (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: send `Content-Type: application/json; charset=utf-8` and assert the behaviour matches the bare `application/json` case
