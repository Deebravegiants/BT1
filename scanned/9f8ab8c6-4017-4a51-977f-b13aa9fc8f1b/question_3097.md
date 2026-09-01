# Q3097: setup? — rotation window unbounded via api_version string

## Question
If an unprivileged attacker submits the `api_version` string, which becomes a directory path in `load_rest_resources` to `setup?`, which only checks that four strings are non-empty, does `Context.setup?` end up acting on a value that was never authenticated, because nothing ever clears `old_api_secret_key`? Close the question on SESSION DERIVATION: a session id is derived only from bytes authenticated under `Context.api_secret_key` and on Critical - cross-user access inside one shop: one staff user's online session is served to another.

## Target
- File/function: `lib/shopify_api/context.rb` -> `Context.setup?`
- Entrypoint: `setup?`, which only checks that four strings are non-empty
- Attacker controls: the `api_version` string, which becomes a directory path in `load_rest_resources`
- Exploit idea: nothing ever clears `old_api_secret_key`
- Invariant to test: SESSION DERIVATION: a session id is derived only from bytes authenticated under `Context.api_secret_key`
- Expected Immunefi impact: Critical - cross-user access inside one shop: one staff user's online session is served to another (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `activate_session` is cleared at the end of a request cycle so a pooled thread cannot serve a stale tenant
