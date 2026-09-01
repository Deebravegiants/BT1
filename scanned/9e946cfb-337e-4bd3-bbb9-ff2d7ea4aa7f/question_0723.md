# Q723: setup? — version becomes a path via api_host vs session.shop

## Question
Does `Context.setup?` collapse two distinct identities into one when an unprivileged attacker submits the `api_host` setting, which splits the connection host from the `Host` header taken from `session.shop` at `setup?`, which only checks that four strings are non-empty? Show that `api_version.gsub("-","_")` is concatenated into a filesystem path before `Dir.exist?`, that AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right is violated, and that the consequence is Critical - authentication bypass: a forged or unsigned request is accepted as authentic by the app.

## Target
- File/function: `lib/shopify_api/context.rb` -> `Context.setup?`
- Entrypoint: `setup?`, which only checks that four strings are non-empty
- Attacker controls: the `api_host` setting, which splits the connection host from the `Host` header taken from `session.shop`
- Exploit idea: `api_version.gsub("-","_")` is concatenated into a filesystem path before `Dir.exist?`
- Invariant to test: AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right
- Expected Immunefi impact: Critical - authentication bypass: a forged or unsigned request is accepted as authentic by the app (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest: run two threads through `Session.temp` and assert neither observes the other's active session
