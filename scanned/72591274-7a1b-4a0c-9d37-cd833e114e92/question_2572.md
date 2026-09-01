# Q2572: setup? — global identity, per-request requests via api_version string

## Question
If an unprivileged attacker submits the `api_version` string, which becomes a directory path in `load_rest_resources` to `setup?`, which only checks that four strings are non-empty, does `Context.setup?` end up acting on a value that was never authenticated, because one process-wide `Context` serves every shop, so any leakage between requests crosses a tenant boundary? Close the question on SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source and on Critical - cross-tenant access: one shop's request reads or mutates another merchant's data.

## Target
- File/function: `lib/shopify_api/context.rb` -> `Context.setup?`
- Entrypoint: `setup?`, which only checks that four strings are non-empty
- Attacker controls: the `api_version` string, which becomes a directory path in `load_rest_resources`
- Exploit idea: one process-wide `Context` serves every shop, so any leakage between requests crosses a tenant boundary
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: Critical - cross-tenant access: one shop's request reads or mutates another merchant's data (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `activate_session` is cleared at the end of a request cycle so a pooled thread cannot serve a stale tenant
