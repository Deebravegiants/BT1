# Q2632: load_rest_resources — global identity, per-request requests via old_api_secret_key

## Question
Can an unprivileged attacker reach `Context.load_rest_resources` through `load_rest_resources(api_version:)`, which builds a filesystem path from the version string and drives a Zeitwerk loader while supplying `old_api_secret_key`, which permanently widens the set of signatures and tokens accepted, so that one process-wide `Context` serves every shop, so any leakage between requests crosses a tenant boundary, breaking the requirement that SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source, and ending in Critical - cross-tenant access: one shop's request reads or mutates another merchant's data?

## Target
- File/function: `lib/shopify_api/context.rb` -> `Context.load_rest_resources`
- Entrypoint: `load_rest_resources(api_version:)`, which builds a filesystem path from the version string and drives a Zeitwerk loader
- Attacker controls: `old_api_secret_key`, which permanently widens the set of signatures and tokens accepted
- Exploit idea: one process-wide `Context` serves every shop, so any leakage between requests crosses a tenant boundary
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: Critical - cross-tenant access: one shop's request reads or mutates another merchant's data (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `activate_session` is cleared at the end of a request cycle so a pooled thread cannot serve a stale tenant
