# Q2752: activate_session — global identity, per-request requests via thread-local session

## Question
Starting from `Context.activate_session(session)` and `Context.active_session`, backed by a `Concurrent::ThreadLocalVar`, can an unprivileged attacker supply the active session under concurrency, where a request handler runs on a pooled thread so that one process-wide `Context` serves every shop, so any leakage between requests crosses a tenant boundary? Determine whether SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source still holds through `Context.activate_session`, and whether the result reaches Critical - cross-tenant access: one shop's request reads or mutates another merchant's data.

## Target
- File/function: `lib/shopify_api/context.rb` -> `Context.activate_session`
- Entrypoint: `Context.activate_session(session)` and `Context.active_session`, backed by a `Concurrent::ThreadLocalVar`
- Attacker controls: the active session under concurrency, where a request handler runs on a pooled thread
- Exploit idea: one process-wide `Context` serves every shop, so any leakage between requests crosses a tenant boundary
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: Critical - cross-tenant access: one shop's request reads or mutates another merchant's data (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `activate_session` is cleared at the end of a request cycle so a pooled thread cannot serve a stale tenant
