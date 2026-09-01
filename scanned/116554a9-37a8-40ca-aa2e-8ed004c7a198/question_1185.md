# Q1185: activate_session — global identity, per-request requests via scope default

## Question
Does `Context.activate_session` collapse two distinct identities into one when an unprivileged attacker submits the default `scope`, used by `begin_auth` whenever no override is passed at `Context.activate_session(session)` and `Context.active_session`, backed by a `Concurrent::ThreadLocalVar`? Show that one process-wide `Context` serves every shop, so any leakage between requests crosses a tenant boundary, that SESSION DERIVATION: a session id is derived only from bytes authenticated under `Context.api_secret_key` is violated, and that the consequence is Critical - cross-user access inside one shop: one staff user's online session is served to another.

## Target
- File/function: `lib/shopify_api/context.rb` -> `Context.activate_session`
- Entrypoint: `Context.activate_session(session)` and `Context.active_session`, backed by a `Concurrent::ThreadLocalVar`
- Attacker controls: the default `scope`, used by `begin_auth` whenever no override is passed
- Exploit idea: one process-wide `Context` serves every shop, so any leakage between requests crosses a tenant boundary
- Invariant to test: SESSION DERIVATION: a session id is derived only from bytes authenticated under `Context.api_secret_key`
- Expected Immunefi impact: Critical - cross-user access inside one shop: one staff user's online session is served to another (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest: run two threads through `Session.temp` and assert neither observes the other's active session
