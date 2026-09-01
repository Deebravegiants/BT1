# Q2812: setup — host header decoupled from connection via thread-local session

## Question
Trace `Context.setup` from `ShopifyAPI::Context.setup(...)`, which stores every security-relevant global including `api_secret_key`, `old_api_secret_key`, `host`, `api_host` and `scope` with the active session under concurrency, where a request handler runs on a pooled thread: because with `api_host` set, `Host` is `session.shop` while the socket goes elsewhere, does the value that was verified stop being the value that is used? Prove the break against SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source and map it to Critical - cross-tenant access: one shop's request reads or mutates another merchant's data.

## Target
- File/function: `lib/shopify_api/context.rb` -> `Context.setup`
- Entrypoint: `ShopifyAPI::Context.setup(...)`, which stores every security-relevant global including `api_secret_key`, `old_api_secret_key`, `host`, `api_host` and `scope`
- Attacker controls: the active session under concurrency, where a request handler runs on a pooled thread
- Exploit idea: with `api_host` set, `Host` is `session.shop` while the socket goes elsewhere
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: Critical - cross-tenant access: one shop's request reads or mutates another merchant's data (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `activate_session` is cleared at the end of a request cycle so a pooled thread cannot serve a stale tenant
