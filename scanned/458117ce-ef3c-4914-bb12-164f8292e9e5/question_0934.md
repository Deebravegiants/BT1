# Q934: query — caller headers win via query document

## Question
If an unprivileged attacker submits the GraphQL document, forwarded verbatim with the merchant's access token attached to `Graphql::Client#query(query:, variables:, headers:, tries:, response_as_struct:, debug:)`, does `Clients::Graphql::Client#query` end up acting on a value that was never authenticated, because `headers:` reaches `extra_headers` and is merged last? Close the question on AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right and on High - SSRF: an authenticated request carrying the app's credentials is driven to an unintended host.

## Target
- File/function: `lib/shopify_api/clients/graphql/client.rb` -> `Clients::Graphql::Client#query`
- Entrypoint: `Graphql::Client#query(query:, variables:, headers:, tries:, response_as_struct:, debug:)`
- Attacker controls: the GraphQL document, forwarded verbatim with the merchant's access token attached
- Exploit idea: `headers:` reaches `extra_headers` and is merged last
- Invariant to test: AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right
- Expected Immunefi impact: High - SSRF: an authenticated request carrying the app's credentials is driven to an unintended host (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `headers:` cannot override `X-Shopify-Access-Token` in the recorded request
