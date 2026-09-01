# Q808: query — caller headers win via variables hash

## Question
If an unprivileged attacker submits the `variables` hash, serialised into the request body to `Graphql::Client#query(query:, variables:, headers:, tries:, response_as_struct:, debug:)`, does `Clients::Graphql::Client#query` end up acting on a value that was never authenticated, because `headers:` reaches `extra_headers` and is merged last? Close the question on AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right and on Critical - cross-tenant access: one shop's request reads or mutates another merchant's data.

## Target
- File/function: `lib/shopify_api/clients/graphql/client.rb` -> `Clients::Graphql::Client#query`
- Entrypoint: `Graphql::Client#query(query:, variables:, headers:, tries:, response_as_struct:, debug:)`
- Attacker controls: the `variables` hash, serialised into the request body
- Exploit idea: `headers:` reaches `extra_headers` and is merged last
- Invariant to test: AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right
- Expected Immunefi impact: Critical - cross-tenant access: one shop's request reads or mutates another merchant's data (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `headers:` cannot override `X-Shopify-Access-Token` in the recorded request
