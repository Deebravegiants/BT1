# Q547: host_name — host header decoupled from connection via api_version string

## Question
Starting from `host_name` / `host_scheme`, which parse `Context.host` (defaulted from `ENV['HOST']`) with `URI`, can an unprivileged attacker supply the `api_version` string, which becomes a directory path in `load_rest_resources` so that with `api_host` set, `Host` is `session.shop` while the socket goes elsewhere? Determine whether AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right still holds through `Context.host_name`, and whether the result reaches Critical - authentication bypass: a forged or unsigned request is accepted as authentic by the app.

## Target
- File/function: `lib/shopify_api/context.rb` -> `Context.host_name`
- Entrypoint: `host_name` / `host_scheme`, which parse `Context.host` (defaulted from `ENV['HOST']`) with `URI`
- Attacker controls: the `api_version` string, which becomes a directory path in `load_rest_resources`
- Exploit idea: with `api_host` set, `Host` is `session.shop` while the socket goes elsewhere
- Invariant to test: AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right
- Expected Immunefi impact: Critical - authentication bypass: a forged or unsigned request is accepted as authentic by the app (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `activate_session` is cleared at the end of a request cycle so a pooled thread cannot serve a stale tenant
