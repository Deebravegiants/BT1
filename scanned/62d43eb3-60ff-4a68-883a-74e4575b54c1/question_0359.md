# Q359: context — tenant identity in every line via log level

## Question
Does `Logger.context` collapse two distinct identities into one when an unprivileged attacker submits the configured `log_level`, which decides whether debug lines carrying request context are emitted at `context`, which embeds `ShopifyAPI::Context.active_session&.shop` in every log line? Show that the shop prefix is derived from thread-local state that may be stale, that CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted is violated, and that the consequence is Critical - cross-tenant access: one shop's request reads or mutates another merchant's data.

## Target
- File/function: `lib/shopify_api/logger.rb` -> `Logger.context`
- Entrypoint: `context`, which embeds `ShopifyAPI::Context.active_session&.shop` in every log line
- Attacker controls: the configured `log_level`, which decides whether debug lines carrying request context are emitted
- Exploit idea: the shop prefix is derived from thread-local state that may be stale
- Invariant to test: CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted
- Expected Immunefi impact: Critical - cross-tenant access: one shop's request reads or mutates another merchant's data (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert the shop prefix matches the shop of the request being served, not a stale thread-local
