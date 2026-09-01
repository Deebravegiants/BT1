# Q1221: load_rest_resources — global identity, per-request requests via rest_disabled

## Question
If an unprivileged attacker submits the `rest_disabled` flag, which decides whether the REST client raises to `load_rest_resources(api_version:)`, which builds a filesystem path from the version string and drives a Zeitwerk loader, does `Context.load_rest_resources` end up acting on a value that was never authenticated, because one process-wide `Context` serves every shop, so any leakage between requests crosses a tenant boundary? Close the question on SESSION DERIVATION: a session id is derived only from bytes authenticated under `Context.api_secret_key` and on Critical - cross-user access inside one shop: one staff user's online session is served to another.

## Target
- File/function: `lib/shopify_api/context.rb` -> `Context.load_rest_resources`
- Entrypoint: `load_rest_resources(api_version:)`, which builds a filesystem path from the version string and drives a Zeitwerk loader
- Attacker controls: the `rest_disabled` flag, which decides whether the REST client raises
- Exploit idea: one process-wide `Context` serves every shop, so any leakage between requests crosses a tenant boundary
- Invariant to test: SESSION DERIVATION: a session id is derived only from bytes authenticated under `Context.api_secret_key`
- Expected Immunefi impact: Critical - cross-user access inside one shop: one staff user's online session is served to another (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest: run two threads through `Session.temp` and assert neither observes the other's active session
