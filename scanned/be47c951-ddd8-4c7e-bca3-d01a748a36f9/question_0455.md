# Q455: activate_session — host header decoupled from connection via api_host vs session.shop

## Question
Can an unprivileged attacker reach `Context.activate_session` through `Context.activate_session(session)` and `Context.active_session`, backed by a `Concurrent::ThreadLocalVar` while supplying the `api_host` setting, which splits the connection host from the `Host` header taken from `session.shop`, so that with `api_host` set, `Host` is `session.shop` while the socket goes elsewhere, breaking the requirement that AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right, and ending in Critical - authentication bypass: a forged or unsigned request is accepted as authentic by the app?

## Target
- File/function: `lib/shopify_api/context.rb` -> `Context.activate_session`
- Entrypoint: `Context.activate_session(session)` and `Context.active_session`, backed by a `Concurrent::ThreadLocalVar`
- Attacker controls: the `api_host` setting, which splits the connection host from the `Host` header taken from `session.shop`
- Exploit idea: with `api_host` set, `Host` is `session.shop` while the socket goes elsewhere
- Invariant to test: AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right
- Expected Immunefi impact: Critical - authentication bypass: a forged or unsigned request is accepted as authentic by the app (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert a crafted `api_version` cannot make `load_rest_resources` touch a path outside `lib/shopify_api/rest/resources`
