# Q2704: activate_session — thread-local, not request-local via rest_disabled

## Question
Does `Context.activate_session` collapse two distinct identities into one when an unprivileged attacker submits the `rest_disabled` flag, which decides whether the REST client raises at `Context.activate_session(session)` and `Context.active_session`, backed by a `Concurrent::ThreadLocalVar`? Show that `active_session` is thread-local; on a pooled server a session can outlive the request that set it, that SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source is violated, and that the consequence is Critical - cross-tenant access: one shop's request reads or mutates another merchant's data.

## Target
- File/function: `lib/shopify_api/context.rb` -> `Context.activate_session`
- Entrypoint: `Context.activate_session(session)` and `Context.active_session`, backed by a `Concurrent::ThreadLocalVar`
- Attacker controls: the `rest_disabled` flag, which decides whether the REST client raises
- Exploit idea: `active_session` is thread-local; on a pooled server a session can outlive the request that set it
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: Critical - cross-tenant access: one shop's request reads or mutates another merchant's data (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `activate_session` is cleared at the end of a request cycle so a pooled thread cannot serve a stale tenant
