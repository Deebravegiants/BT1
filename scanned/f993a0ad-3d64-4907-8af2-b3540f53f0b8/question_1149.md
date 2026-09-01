# Q1149: load_rest_resources — version becomes a path via old_api_secret_key

## Question
Starting from `load_rest_resources(api_version:)`, which builds a filesystem path from the version string and drives a Zeitwerk loader, can an unprivileged attacker supply `old_api_secret_key`, which permanently widens the set of signatures and tokens accepted so that `api_version.gsub("-","_")` is concatenated into a filesystem path before `Dir.exist?`? Determine whether SESSION DERIVATION: a session id is derived only from bytes authenticated under `Context.api_secret_key` still holds through `Context.load_rest_resources`, and whether the result reaches Critical - cross-user access inside one shop: one staff user's online session is served to another.

## Target
- File/function: `lib/shopify_api/context.rb` -> `Context.load_rest_resources`
- Entrypoint: `load_rest_resources(api_version:)`, which builds a filesystem path from the version string and drives a Zeitwerk loader
- Attacker controls: `old_api_secret_key`, which permanently widens the set of signatures and tokens accepted
- Exploit idea: `api_version.gsub("-","_")` is concatenated into a filesystem path before `Dir.exist?`
- Invariant to test: SESSION DERIVATION: a session id is derived only from bytes authenticated under `Context.api_secret_key`
- Expected Immunefi impact: Critical - cross-user access inside one shop: one staff user's online session is served to another (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest: run two threads through `Session.temp` and assert neither observes the other's active session
