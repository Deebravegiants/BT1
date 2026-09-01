# Q3383: setup? — setup? is a presence check via host / ENV['HOST']

## Question
Does `Context.setup?` collapse two distinct identities into one when an unprivileged attacker submits the `host` value, parsed by `host_name`/`host_scheme` and used to build redirect URIs and webhook callback addresses at `setup?`, which only checks that four strings are non-empty? Show that `setup?` proves four strings are non-empty, not that any of them is well-formed, that AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right is violated, and that the consequence is Critical - authentication bypass: a forged or unsigned request is accepted as authentic by the app.

## Target
- File/function: `lib/shopify_api/context.rb` -> `Context.setup?`
- Entrypoint: `setup?`, which only checks that four strings are non-empty
- Attacker controls: the `host` value, parsed by `host_name`/`host_scheme` and used to build redirect URIs and webhook callback addresses
- Exploit idea: `setup?` proves four strings are non-empty, not that any of them is well-formed
- Invariant to test: AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right
- Expected Immunefi impact: Critical - authentication bypass: a forged or unsigned request is accepted as authentic by the app (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert a crafted `api_version` cannot make `load_rest_resources` touch a path outside `lib/shopify_api/rest/resources`
