# Q1035: activate_session — host header decoupled from connection via thread-local session

## Question
Is there a reachable state in which an unprivileged attacker, controlling the active session under concurrency, where a request handler runs on a pooled thread at `Context.activate_session(session)` and `Context.active_session`, backed by a `Concurrent::ThreadLocalVar`, makes `Context.activate_session` return a result the caller treats as authenticated, given that with `api_host` set, `Host` is `session.shop` while the socket goes elsewhere? Test AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right and quantify Critical - authentication bypass: a forged or unsigned request is accepted as authentic by the app.

## Target
- File/function: `lib/shopify_api/context.rb` -> `Context.activate_session`
- Entrypoint: `Context.activate_session(session)` and `Context.active_session`, backed by a `Concurrent::ThreadLocalVar`
- Attacker controls: the active session under concurrency, where a request handler runs on a pooled thread
- Exploit idea: with `api_host` set, `Host` is `session.shop` while the socket goes elsewhere
- Invariant to test: AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right
- Expected Immunefi impact: Critical - authentication bypass: a forged or unsigned request is accepted as authentic by the app (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest: run two threads through `Session.temp` and assert neither observes the other's active session
