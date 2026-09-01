# Q2248: activate_session — rotation window unbounded via host / ENV['HOST']

## Question
Starting from `Context.activate_session(session)` and `Context.active_session`, backed by a `Concurrent::ThreadLocalVar`, can an unprivileged attacker supply the `host` value, parsed by `host_name`/`host_scheme` and used to build redirect URIs and webhook callback addresses so that nothing ever clears `old_api_secret_key`? Determine whether SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source still holds through `Context.activate_session`, and whether the result reaches Critical - cross-tenant access: one shop's request reads or mutates another merchant's data.

## Target
- File/function: `lib/shopify_api/context.rb` -> `Context.activate_session`
- Entrypoint: `Context.activate_session(session)` and `Context.active_session`, backed by a `Concurrent::ThreadLocalVar`
- Attacker controls: the `host` value, parsed by `host_name`/`host_scheme` and used to build redirect URIs and webhook callback addresses
- Exploit idea: nothing ever clears `old_api_secret_key`
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: Critical - cross-tenant access: one shop's request reads or mutates another merchant's data (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `activate_session` is cleared at the end of a request cycle so a pooled thread cannot serve a stale tenant
