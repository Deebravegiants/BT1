# Q127: query — no operation policy via variables hash

## Question
Starting from `Graphql::Client#query(query:, variables:, headers:, tries:, response_as_struct:, debug:)`, can an unprivileged attacker supply the `variables` hash, serialised into the request body so that no distinction between queries and mutations, and no scope check against the session? Determine whether AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right still holds through `Clients::Graphql::Client#query`, and whether the result reaches High - scope or expiry check bypass granting an operation the session was never authorized for.

## Target
- File/function: `lib/shopify_api/clients/graphql/client.rb` -> `Clients::Graphql::Client#query`
- Entrypoint: `Graphql::Client#query(query:, variables:, headers:, tries:, response_as_struct:, debug:)`
- Attacker controls: the `variables` hash, serialised into the request body
- Exploit idea: no distinction between queries and mutations, and no scope check against the session
- Invariant to test: AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right
- Expected Immunefi impact: High - scope or expiry check bypass granting an operation the session was never authorized for (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `headers:` cannot override `X-Shopify-Access-Token` in the recorded request
