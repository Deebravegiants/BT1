# Q307: query — OpenStruct re-parse via response_as_struct

## Question
Is there a reachable state in which an unprivileged attacker, controlling the `response_as_struct` flag, which re-parses the body into `OpenStruct` objects at `Graphql::Client#query(query:, variables:, headers:, tries:, response_as_struct:, debug:)`, makes `Clients::Graphql::Client#query` return a result the caller treats as authenticated, given that re-parsing response JSON into `OpenStruct` creates dynamically named accessors from response-controlled keys? Test AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right and quantify High - scope or expiry check bypass granting an operation the session was never authorized for.

## Target
- File/function: `lib/shopify_api/clients/graphql/client.rb` -> `Clients::Graphql::Client#query`
- Entrypoint: `Graphql::Client#query(query:, variables:, headers:, tries:, response_as_struct:, debug:)`
- Attacker controls: the `response_as_struct` flag, which re-parses the body into `OpenStruct` objects
- Exploit idea: re-parsing response JSON into `OpenStruct` creates dynamically named accessors from response-controlled keys
- Invariant to test: AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right
- Expected Immunefi impact: High - scope or expiry check bypass granting an operation the session was never authorized for (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `headers:` cannot override `X-Shopify-Access-Token` in the recorded request
