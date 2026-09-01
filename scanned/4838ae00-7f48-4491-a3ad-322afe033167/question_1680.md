# Q1680: load_rest_resources — setup? is a presence check via thread-local session

## Question
Can an unprivileged attacker reach `Context.load_rest_resources` through `load_rest_resources(api_version:)`, which builds a filesystem path from the version string and drives a Zeitwerk loader while supplying the active session under concurrency, where a request handler runs on a pooled thread, so that `setup?` proves four strings are non-empty, not that any of them is well-formed, breaking the requirement that SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source, and ending in Critical - cross-tenant access: one shop's request reads or mutates another merchant's data?

## Target
- File/function: `lib/shopify_api/context.rb` -> `Context.load_rest_resources`
- Entrypoint: `load_rest_resources(api_version:)`, which builds a filesystem path from the version string and drives a Zeitwerk loader
- Attacker controls: the active session under concurrency, where a request handler runs on a pooled thread
- Exploit idea: `setup?` proves four strings are non-empty, not that any of them is well-formed
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: Critical - cross-tenant access: one shop's request reads or mutates another merchant's data (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest: run two threads through `Session.temp` and assert neither observes the other's active session
