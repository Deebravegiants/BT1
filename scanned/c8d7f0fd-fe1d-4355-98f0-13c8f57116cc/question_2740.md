# Q2740: activate_session — rotation window unbounded via scope default

## Question
If an unprivileged attacker submits the default `scope`, used by `begin_auth` whenever no override is passed to `Context.activate_session(session)` and `Context.active_session`, backed by a `Concurrent::ThreadLocalVar`, does `Context.activate_session` end up acting on a value that was never authenticated, because nothing ever clears `old_api_secret_key`? Close the question on SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source and on Critical - cross-tenant access: one shop's request reads or mutates another merchant's data.

## Target
- File/function: `lib/shopify_api/context.rb` -> `Context.activate_session`
- Entrypoint: `Context.activate_session(session)` and `Context.active_session`, backed by a `Concurrent::ThreadLocalVar`
- Attacker controls: the default `scope`, used by `begin_auth` whenever no override is passed
- Exploit idea: nothing ever clears `old_api_secret_key`
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: Critical - cross-tenant access: one shop's request reads or mutates another merchant's data (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `activate_session` is cleared at the end of a request cycle so a pooled thread cannot serve a stale tenant
