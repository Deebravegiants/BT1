# Q454: query — no operation policy via query document

## Question
Is there a reachable state in which an unprivileged attacker, controlling the GraphQL document, forwarded verbatim with the merchant's access token attached at `Graphql::Client#query(query:, variables:, headers:, tries:, response_as_struct:, debug:)`, makes `Clients::Graphql::Client#query` return a result the caller treats as authenticated, given that no distinction between queries and mutations, and no scope check against the session? Test AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right and quantify High - SSRF: an authenticated request carrying the app's credentials is driven to an unintended host.

## Target
- File/function: `lib/shopify_api/clients/graphql/client.rb` -> `Clients::Graphql::Client#query`
- Entrypoint: `Graphql::Client#query(query:, variables:, headers:, tries:, response_as_struct:, debug:)`
- Attacker controls: the GraphQL document, forwarded verbatim with the merchant's access token attached
- Exploit idea: no distinction between queries and mutations, and no scope check against the session
- Invariant to test: AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right
- Expected Immunefi impact: High - SSRF: an authenticated request carrying the app's credentials is driven to an unintended host (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `headers:` cannot override `X-Shopify-Access-Token` in the recorded request
