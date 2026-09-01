# Q333: load_rest_resources — version becomes a path via host / ENV['HOST']

## Question
Can the `host` value, parsed by `host_name`/`host_scheme` and used to build redirect URIs and webhook callback addresses, supplied by an unprivileged attacker at `load_rest_resources(api_version:)`, which builds a filesystem path from the version string and drives a Zeitwerk loader, make `Context.load_rest_resources` and the code consuming its result disagree, given that `api_version.gsub("-","_")` is concatenated into a filesystem path before `Dir.exist?`? The binding to test is SESSION DERIVATION: a session id is derived only from bytes authenticated under `Context.api_secret_key`; the impact to prove is Critical - cross-user access inside one shop: one staff user's online session is served to another.

## Target
- File/function: `lib/shopify_api/context.rb` -> `Context.load_rest_resources`
- Entrypoint: `load_rest_resources(api_version:)`, which builds a filesystem path from the version string and drives a Zeitwerk loader
- Attacker controls: the `host` value, parsed by `host_name`/`host_scheme` and used to build redirect URIs and webhook callback addresses
- Exploit idea: `api_version.gsub("-","_")` is concatenated into a filesystem path before `Dir.exist?`
- Invariant to test: SESSION DERIVATION: a session id is derived only from bytes authenticated under `Context.api_secret_key`
- Expected Immunefi impact: Critical - cross-user access inside one shop: one staff user's online session is served to another (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest: run two threads through `Session.temp` and assert neither observes the other's active session
