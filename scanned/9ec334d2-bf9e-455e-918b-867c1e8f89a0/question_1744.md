# Q1744: host_name — global identity, per-request requests via api_version string

## Question
Starting from `host_name` / `host_scheme`, which parse `Context.host` (defaulted from `ENV['HOST']`) with `URI`, can an unprivileged attacker supply the `api_version` string, which becomes a directory path in `load_rest_resources` so that one process-wide `Context` serves every shop, so any leakage between requests crosses a tenant boundary? Determine whether SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source still holds through `Context.host_name`, and whether the result reaches Critical - cross-tenant access: one shop's request reads or mutates another merchant's data.

## Target
- File/function: `lib/shopify_api/context.rb` -> `Context.host_name`
- Entrypoint: `host_name` / `host_scheme`, which parse `Context.host` (defaulted from `ENV['HOST']`) with `URI`
- Attacker controls: the `api_version` string, which becomes a directory path in `load_rest_resources`
- Exploit idea: one process-wide `Context` serves every shop, so any leakage between requests crosses a tenant boundary
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: Critical - cross-tenant access: one shop's request reads or mutates another merchant's data (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `activate_session` is cleared at the end of a request cycle so a pooled thread cannot serve a stale tenant
