# Q2668: load_rest_resources — setup? is a presence check via old_api_secret_key

## Question
Starting from `load_rest_resources(api_version:)`, which builds a filesystem path from the version string and drives a Zeitwerk loader, can an unprivileged attacker supply `old_api_secret_key`, which permanently widens the set of signatures and tokens accepted so that `setup?` proves four strings are non-empty, not that any of them is well-formed? Determine whether SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source still holds through `Context.load_rest_resources`, and whether the result reaches Critical - cross-tenant access: one shop's request reads or mutates another merchant's data.

## Target
- File/function: `lib/shopify_api/context.rb` -> `Context.load_rest_resources`
- Entrypoint: `load_rest_resources(api_version:)`, which builds a filesystem path from the version string and drives a Zeitwerk loader
- Attacker controls: `old_api_secret_key`, which permanently widens the set of signatures and tokens accepted
- Exploit idea: `setup?` proves four strings are non-empty, not that any of them is well-formed
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: Critical - cross-tenant access: one shop's request reads or mutates another merchant's data (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `activate_session` is cleared at the end of a request cycle so a pooled thread cannot serve a stale tenant
