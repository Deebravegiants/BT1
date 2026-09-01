# Q568: initialize — no operation policy via response_as_struct

## Question
Starting from `Graphql::Client.new(session:, base_path:, api_version:)` and its version-override branch, can an unprivileged attacker supply the `response_as_struct` flag, which re-parses the body into `OpenStruct` objects so that no distinction between queries and mutations, and no scope check against the session? Determine whether AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right still holds through `Clients::Graphql::Client#initialize`, and whether the result reaches Critical - cross-tenant access: one shop's request reads or mutates another merchant's data.

## Target
- File/function: `lib/shopify_api/clients/graphql/client.rb` -> `Clients::Graphql::Client#initialize`
- Entrypoint: `Graphql::Client.new(session:, base_path:, api_version:)` and its version-override branch
- Attacker controls: the `response_as_struct` flag, which re-parses the body into `OpenStruct` objects
- Exploit idea: no distinction between queries and mutations, and no scope check against the session
- Invariant to test: AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right
- Expected Immunefi impact: Critical - cross-tenant access: one shop's request reads or mutates another merchant's data (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `headers:` cannot override `X-Shopify-Access-Token` in the recorded request
