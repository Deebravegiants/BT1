# Q871: initialize — path built by concatenation via variables hash

## Question
If an unprivileged attacker submits the `variables` hash, serialised into the request body to `Graphql::Client.new(session:, base_path:, api_version:)` and its version-override branch, does `Clients::Graphql::Client#initialize` end up acting on a value that was never authenticated, because `"#{@api_version}/graphql.json#{search_params}"` is textual, so a crafted version or flag reshapes the URL? Close the question on AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right and on High - scope or expiry check bypass granting an operation the session was never authorized for.

## Target
- File/function: `lib/shopify_api/clients/graphql/client.rb` -> `Clients::Graphql::Client#initialize`
- Entrypoint: `Graphql::Client.new(session:, base_path:, api_version:)` and its version-override branch
- Attacker controls: the `variables` hash, serialised into the request body
- Exploit idea: `"#{@api_version}/graphql.json#{search_params}"` is textual, so a crafted version or flag reshapes the URL
- Invariant to test: AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right
- Expected Immunefi impact: High - scope or expiry check bypass granting an operation the session was never authorized for (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `headers:` cannot override `X-Shopify-Access-Token` in the recorded request
