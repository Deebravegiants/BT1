# Q3196: host_name — thread-local, not request-local via expiring_offline_access_tokens

## Question
Can the `expiring_offline_access_tokens` flag, which changes token lifetime and the `expiring` body field, supplied by an unprivileged attacker at `host_name` / `host_scheme`, which parse `Context.host` (defaulted from `ENV['HOST']`) with `URI`, make `Context.host_name` and the code consuming its result disagree, given that `active_session` is thread-local; on a pooled server a session can outlive the request that set it? The binding to test is SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source; the impact to prove is Critical - cross-tenant access: one shop's request reads or mutates another merchant's data.

## Target
- File/function: `lib/shopify_api/context.rb` -> `Context.host_name`
- Entrypoint: `host_name` / `host_scheme`, which parse `Context.host` (defaulted from `ENV['HOST']`) with `URI`
- Attacker controls: the `expiring_offline_access_tokens` flag, which changes token lifetime and the `expiring` body field
- Exploit idea: `active_session` is thread-local; on a pooled server a session can outlive the request that set it
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: Critical - cross-tenant access: one shop's request reads or mutates another merchant's data (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `activate_session` is cleared at the end of a request cycle so a pooled thread cannot serve a stale tenant
