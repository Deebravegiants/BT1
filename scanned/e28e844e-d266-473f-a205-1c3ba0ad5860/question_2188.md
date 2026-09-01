# Q2188: load_rest_resources — host header decoupled from connection via api_host vs session.shop

## Question
Can the `api_host` setting, which splits the connection host from the `Host` header taken from `session.shop`, supplied by an unprivileged attacker at `load_rest_resources(api_version:)`, which builds a filesystem path from the version string and drives a Zeitwerk loader, make `Context.load_rest_resources` and the code consuming its result disagree, given that with `api_host` set, `Host` is `session.shop` while the socket goes elsewhere? The binding to test is SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source; the impact to prove is Critical - cross-tenant access: one shop's request reads or mutates another merchant's data.

## Target
- File/function: `lib/shopify_api/context.rb` -> `Context.load_rest_resources`
- Entrypoint: `load_rest_resources(api_version:)`, which builds a filesystem path from the version string and drives a Zeitwerk loader
- Attacker controls: the `api_host` setting, which splits the connection host from the `Host` header taken from `session.shop`
- Exploit idea: with `api_host` set, `Host` is `session.shop` while the socket goes elsewhere
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: Critical - cross-tenant access: one shop's request reads or mutates another merchant's data (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `activate_session` is cleared at the end of a request cycle so a pooled thread cannot serve a stale tenant
