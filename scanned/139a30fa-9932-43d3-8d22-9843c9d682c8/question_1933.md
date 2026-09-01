# Q1933: load_rest_resources — rotation window unbounded via rest_disabled

## Question
Starting from `load_rest_resources(api_version:)`, which builds a filesystem path from the version string and drives a Zeitwerk loader, can an unprivileged attacker supply the `rest_disabled` flag, which decides whether the REST client raises so that nothing ever clears `old_api_secret_key`? Determine whether SESSION DERIVATION: a session id is derived only from bytes authenticated under `Context.api_secret_key` still holds through `Context.load_rest_resources`, and whether the result reaches Critical - cross-user access inside one shop: one staff user's online session is served to another.

## Target
- File/function: `lib/shopify_api/context.rb` -> `Context.load_rest_resources`
- Entrypoint: `load_rest_resources(api_version:)`, which builds a filesystem path from the version string and drives a Zeitwerk loader
- Attacker controls: the `rest_disabled` flag, which decides whether the REST client raises
- Exploit idea: nothing ever clears `old_api_secret_key`
- Invariant to test: SESSION DERIVATION: a session id is derived only from bytes authenticated under `Context.api_secret_key`
- Expected Immunefi impact: Critical - cross-user access inside one shop: one staff user's online session is served to another (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `activate_session` is cleared at the end of a request cycle so a pooled thread cannot serve a stale tenant
