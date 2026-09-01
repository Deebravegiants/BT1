# Q2495: host_name — host header decoupled from connection via expiring_offline_access_tokens

## Question
If an unprivileged attacker submits the `expiring_offline_access_tokens` flag, which changes token lifetime and the `expiring` body field to `host_name` / `host_scheme`, which parse `Context.host` (defaulted from `ENV['HOST']`) with `URI`, does `Context.host_name` end up acting on a value that was never authenticated, because with `api_host` set, `Host` is `session.shop` while the socket goes elsewhere? Close the question on AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right and on Critical - authentication bypass: a forged or unsigned request is accepted as authentic by the app.

## Target
- File/function: `lib/shopify_api/context.rb` -> `Context.host_name`
- Entrypoint: `host_name` / `host_scheme`, which parse `Context.host` (defaulted from `ENV['HOST']`) with `URI`
- Attacker controls: the `expiring_offline_access_tokens` flag, which changes token lifetime and the `expiring` body field
- Exploit idea: with `api_host` set, `Host` is `session.shop` while the socket goes elsewhere
- Invariant to test: AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right
- Expected Immunefi impact: Critical - authentication bypass: a forged or unsigned request is accepted as authentic by the app (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert a crafted `api_version` cannot make `load_rest_resources` touch a path outside `lib/shopify_api/rest/resources`
