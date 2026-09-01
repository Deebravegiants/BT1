# Q3361: activate_session — setup? is a presence check via api_version string

## Question
Starting from `Context.activate_session(session)` and `Context.active_session`, backed by a `Concurrent::ThreadLocalVar`, can an unprivileged attacker supply the `api_version` string, which becomes a directory path in `load_rest_resources` so that `setup?` proves four strings are non-empty, not that any of them is well-formed? Determine whether SESSION DERIVATION: a session id is derived only from bytes authenticated under `Context.api_secret_key` still holds through `Context.activate_session`, and whether the result reaches Critical - cross-user access inside one shop: one staff user's online session is served to another.

## Target
- File/function: `lib/shopify_api/context.rb` -> `Context.activate_session`
- Entrypoint: `Context.activate_session(session)` and `Context.active_session`, backed by a `Concurrent::ThreadLocalVar`
- Attacker controls: the `api_version` string, which becomes a directory path in `load_rest_resources`
- Exploit idea: `setup?` proves four strings are non-empty, not that any of them is well-formed
- Invariant to test: SESSION DERIVATION: a session id is derived only from bytes authenticated under `Context.api_secret_key`
- Expected Immunefi impact: Critical - cross-user access inside one shop: one staff user's online session is served to another (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `activate_session` is cleared at the end of a request cycle so a pooled thread cannot serve a stale tenant
