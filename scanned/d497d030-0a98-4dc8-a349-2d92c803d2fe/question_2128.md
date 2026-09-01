# Q2128: setup — host header decoupled from connection via host / ENV['HOST']

## Question
Can an unprivileged attacker reach `Context.setup` through `ShopifyAPI::Context.setup(...)`, which stores every security-relevant global including `api_secret_key`, `old_api_secret_key`, `host`, `api_host` and `scope` while supplying the `host` value, parsed by `host_name`/`host_scheme` and used to build redirect URIs and webhook callback addresses, so that with `api_host` set, `Host` is `session.shop` while the socket goes elsewhere, breaking the requirement that SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source, and ending in Critical - cross-tenant access: one shop's request reads or mutates another merchant's data?

## Target
- File/function: `lib/shopify_api/context.rb` -> `Context.setup`
- Entrypoint: `ShopifyAPI::Context.setup(...)`, which stores every security-relevant global including `api_secret_key`, `old_api_secret_key`, `host`, `api_host` and `scope`
- Attacker controls: the `host` value, parsed by `host_name`/`host_scheme` and used to build redirect URIs and webhook callback addresses
- Exploit idea: with `api_host` set, `Host` is `session.shop` while the socket goes elsewhere
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: Critical - cross-tenant access: one shop's request reads or mutates another merchant's data (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `activate_session` is cleared at the end of a request cycle so a pooled thread cannot serve a stale tenant
