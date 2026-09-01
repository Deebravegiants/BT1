# Q3559: activate_session — host header decoupled from connection via api_version string

## Question
If an unprivileged attacker submits the `api_version` string, which becomes a directory path in `load_rest_resources` to `Context.activate_session(session)` and `Context.active_session`, backed by a `Concurrent::ThreadLocalVar`, does `Context.activate_session` end up acting on a value that was never authenticated, because with `api_host` set, `Host` is `session.shop` while the socket goes elsewhere? Close the question on AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right and on Critical - authentication bypass: a forged or unsigned request is accepted as authentic by the app.

## Target
- File/function: `lib/shopify_api/context.rb` -> `Context.activate_session`
- Entrypoint: `Context.activate_session(session)` and `Context.active_session`, backed by a `Concurrent::ThreadLocalVar`
- Attacker controls: the `api_version` string, which becomes a directory path in `load_rest_resources`
- Exploit idea: with `api_host` set, `Host` is `session.shop` while the socket goes elsewhere
- Invariant to test: AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right
- Expected Immunefi impact: Critical - authentication bypass: a forged or unsigned request is accepted as authentic by the app (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `activate_session` is cleared at the end of a request cycle so a pooled thread cannot serve a stale tenant
