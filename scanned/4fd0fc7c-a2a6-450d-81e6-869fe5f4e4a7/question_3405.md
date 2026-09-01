# Q3405: setup? — version becomes a path via thread-local session

## Question
If an unprivileged attacker submits the active session under concurrency, where a request handler runs on a pooled thread to `setup?`, which only checks that four strings are non-empty, does `Context.setup?` end up acting on a value that was never authenticated, because `api_version.gsub("-","_")` is concatenated into a filesystem path before `Dir.exist?`? Close the question on SESSION DERIVATION: a session id is derived only from bytes authenticated under `Context.api_secret_key` and on Critical - cross-user access inside one shop: one staff user's online session is served to another.

## Target
- File/function: `lib/shopify_api/context.rb` -> `Context.setup?`
- Entrypoint: `setup?`, which only checks that four strings are non-empty
- Attacker controls: the active session under concurrency, where a request handler runs on a pooled thread
- Exploit idea: `api_version.gsub("-","_")` is concatenated into a filesystem path before `Dir.exist?`
- Invariant to test: SESSION DERIVATION: a session id is derived only from bytes authenticated under `Context.api_secret_key`
- Expected Immunefi impact: Critical - cross-user access inside one shop: one staff user's online session is served to another (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest: run two threads through `Session.temp` and assert neither observes the other's active session
