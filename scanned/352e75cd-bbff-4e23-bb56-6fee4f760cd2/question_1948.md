# Q1948: load_rest_resources — thread-local, not request-local via scope default

## Question
Does `Context.load_rest_resources` collapse two distinct identities into one when an unprivileged attacker submits the default `scope`, used by `begin_auth` whenever no override is passed at `load_rest_resources(api_version:)`, which builds a filesystem path from the version string and drives a Zeitwerk loader? Show that `active_session` is thread-local; on a pooled server a session can outlive the request that set it, that SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source is violated, and that the consequence is Critical - cross-tenant access: one shop's request reads or mutates another merchant's data.

## Target
- File/function: `lib/shopify_api/context.rb` -> `Context.load_rest_resources`
- Entrypoint: `load_rest_resources(api_version:)`, which builds a filesystem path from the version string and drives a Zeitwerk loader
- Attacker controls: the default `scope`, used by `begin_auth` whenever no override is passed
- Exploit idea: `active_session` is thread-local; on a pooled server a session can outlive the request that set it
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: Critical - cross-tenant access: one shop's request reads or mutates another merchant's data (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `activate_session` is cleared at the end of a request cycle so a pooled thread cannot serve a stale tenant
