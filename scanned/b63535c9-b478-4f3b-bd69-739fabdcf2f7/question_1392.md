# Q1392: load_rest_resources — thread-local, not request-local via expiring_offline_access_tokens

## Question
Is there a reachable state in which an unprivileged attacker, controlling the `expiring_offline_access_tokens` flag, which changes token lifetime and the `expiring` body field at `load_rest_resources(api_version:)`, which builds a filesystem path from the version string and drives a Zeitwerk loader, makes `Context.load_rest_resources` return a result the caller treats as authenticated, given that `active_session` is thread-local; on a pooled server a session can outlive the request that set it? Test SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source and quantify Critical - cross-tenant access: one shop's request reads or mutates another merchant's data.

## Target
- File/function: `lib/shopify_api/context.rb` -> `Context.load_rest_resources`
- Entrypoint: `load_rest_resources(api_version:)`, which builds a filesystem path from the version string and drives a Zeitwerk loader
- Attacker controls: the `expiring_offline_access_tokens` flag, which changes token lifetime and the `expiring` body field
- Exploit idea: `active_session` is thread-local; on a pooled server a session can outlive the request that set it
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: Critical - cross-tenant access: one shop's request reads or mutates another merchant's data (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest: run two threads through `Session.temp` and assert neither observes the other's active session
