# Q3493: load_rest_resources — global identity, per-request requests via api_version string

## Question
Can an unprivileged attacker reach `Context.load_rest_resources` through `load_rest_resources(api_version:)`, which builds a filesystem path from the version string and drives a Zeitwerk loader while supplying the `api_version` string, which becomes a directory path in `load_rest_resources`, so that one process-wide `Context` serves every shop, so any leakage between requests crosses a tenant boundary, breaking the requirement that SESSION DERIVATION: a session id is derived only from bytes authenticated under `Context.api_secret_key`, and ending in Critical - cross-user access inside one shop: one staff user's online session is served to another?

## Target
- File/function: `lib/shopify_api/context.rb` -> `Context.load_rest_resources`
- Entrypoint: `load_rest_resources(api_version:)`, which builds a filesystem path from the version string and drives a Zeitwerk loader
- Attacker controls: the `api_version` string, which becomes a directory path in `load_rest_resources`
- Exploit idea: one process-wide `Context` serves every shop, so any leakage between requests crosses a tenant boundary
- Invariant to test: SESSION DERIVATION: a session id is derived only from bytes authenticated under `Context.api_secret_key`
- Expected Immunefi impact: Critical - cross-user access inside one shop: one staff user's online session is served to another (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `activate_session` is cleared at the end of a request cycle so a pooled thread cannot serve a stale tenant
