# Q3251: setup? — setup? is a presence check via scope default

## Question
If an unprivileged attacker submits the default `scope`, used by `begin_auth` whenever no override is passed to `setup?`, which only checks that four strings are non-empty, does `Context.setup?` end up acting on a value that was never authenticated, because `setup?` proves four strings are non-empty, not that any of them is well-formed? Close the question on AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right and on Critical - authentication bypass: a forged or unsigned request is accepted as authentic by the app.

## Target
- File/function: `lib/shopify_api/context.rb` -> `Context.setup?`
- Entrypoint: `setup?`, which only checks that four strings are non-empty
- Attacker controls: the default `scope`, used by `begin_auth` whenever no override is passed
- Exploit idea: `setup?` proves four strings are non-empty, not that any of them is well-formed
- Invariant to test: AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right
- Expected Immunefi impact: Critical - authentication bypass: a forged or unsigned request is accepted as authentic by the app (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert a crafted `api_version` cannot make `load_rest_resources` touch a path outside `lib/shopify_api/rest/resources`
