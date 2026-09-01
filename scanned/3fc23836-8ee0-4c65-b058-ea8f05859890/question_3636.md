# Q3636: load_rest_resources — thread-local, not request-local via thread-local session

## Question
If an unprivileged attacker submits the active session under concurrency, where a request handler runs on a pooled thread to `load_rest_resources(api_version:)`, which builds a filesystem path from the version string and drives a Zeitwerk loader, does `Context.load_rest_resources` end up acting on a value that was never authenticated, because `active_session` is thread-local; on a pooled server a session can outlive the request that set it? Close the question on SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source and on Critical - cross-tenant access: one shop's request reads or mutates another merchant's data.

## Target
- File/function: `lib/shopify_api/context.rb` -> `Context.load_rest_resources`
- Entrypoint: `load_rest_resources(api_version:)`, which builds a filesystem path from the version string and drives a Zeitwerk loader
- Attacker controls: the active session under concurrency, where a request handler runs on a pooled thread
- Exploit idea: `active_session` is thread-local; on a pooled server a session can outlive the request that set it
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: Critical - cross-tenant access: one shop's request reads or mutates another merchant's data (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest: run two threads through `Session.temp` and assert neither observes the other's active session
