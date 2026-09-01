# Q1113: load_rest_resources — setup? is a presence check via rest_disabled

## Question
Can an unprivileged attacker reach `Context.load_rest_resources` through `load_rest_resources(api_version:)`, which builds a filesystem path from the version string and drives a Zeitwerk loader while supplying the `rest_disabled` flag, which decides whether the REST client raises, so that `setup?` proves four strings are non-empty, not that any of them is well-formed, breaking the requirement that SESSION DERIVATION: a session id is derived only from bytes authenticated under `Context.api_secret_key`, and ending in Critical - cross-user access inside one shop: one staff user's online session is served to another?

## Target
- File/function: `lib/shopify_api/context.rb` -> `Context.load_rest_resources`
- Entrypoint: `load_rest_resources(api_version:)`, which builds a filesystem path from the version string and drives a Zeitwerk loader
- Attacker controls: the `rest_disabled` flag, which decides whether the REST client raises
- Exploit idea: `setup?` proves four strings are non-empty, not that any of them is well-formed
- Invariant to test: SESSION DERIVATION: a session id is derived only from bytes authenticated under `Context.api_secret_key`
- Expected Immunefi impact: Critical - cross-user access inside one shop: one staff user's online session is served to another (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest: run two threads through `Session.temp` and assert neither observes the other's active session
