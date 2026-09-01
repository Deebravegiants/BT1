# Q2716: host_name — rotation window unbounded via expiring_offline_access_tokens

## Question
Can an unprivileged attacker reach `Context.host_name` through `host_name` / `host_scheme`, which parse `Context.host` (defaulted from `ENV['HOST']`) with `URI` while supplying the `expiring_offline_access_tokens` flag, which changes token lifetime and the `expiring` body field, so that nothing ever clears `old_api_secret_key`, breaking the requirement that SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source, and ending in Critical - cross-tenant access: one shop's request reads or mutates another merchant's data?

## Target
- File/function: `lib/shopify_api/context.rb` -> `Context.host_name`
- Entrypoint: `host_name` / `host_scheme`, which parse `Context.host` (defaulted from `ENV['HOST']`) with `URI`
- Attacker controls: the `expiring_offline_access_tokens` flag, which changes token lifetime and the `expiring` body field
- Exploit idea: nothing ever clears `old_api_secret_key`
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: Critical - cross-tenant access: one shop's request reads or mutates another merchant's data (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `activate_session` is cleared at the end of a request cycle so a pooled thread cannot serve a stale tenant
