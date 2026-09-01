# Q672: build_check_query — re-register decision from response via path with scheme

## Question
Can an unprivileged attacker reach `Registrations::Http#build_check_query` through `build_check_query`, which interpolates `@topic` into a GraphQL document while supplying a registration `path` already carrying `http://` or `https://`, returned verbatim as the callback address, so that whether the callback address is overwritten is decided by comparing against attacker-influenceable response content, breaking the requirement that CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted, and ending in Critical - cross-tenant access: one shop's request reads or mutates another merchant's data?

## Target
- File/function: `lib/shopify_api/webhooks/registrations/http.rb` -> `Registrations::Http#build_check_query`
- Entrypoint: `build_check_query`, which interpolates `@topic` into a GraphQL document
- Attacker controls: a registration `path` already carrying `http://` or `https://`, returned verbatim as the callback address
- Exploit idea: whether the callback address is overwritten is decided by comparing against attacker-influenceable response content
- Invariant to test: CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted
- Expected Immunefi impact: Critical - cross-tenant access: one shop's request reads or mutates another merchant's data (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest: set `Context.host_name` and assert `callback_address` rejects a path whose prefix merely matches it
