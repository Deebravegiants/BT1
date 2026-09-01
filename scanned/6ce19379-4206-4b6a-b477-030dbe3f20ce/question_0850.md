# Q850: query — path built by concatenation via debug flag

## Question
If an unprivileged attacker submits the `debug:` flag, which appends `?debug=true` to the path by string concatenation to `Graphql::Client#query(query:, variables:, headers:, tries:, response_as_struct:, debug:)`, does `Clients::Graphql::Client#query` end up acting on a value that was never authenticated, because `"#{@api_version}/graphql.json#{search_params}"` is textual, so a crafted version or flag reshapes the URL? Close the question on AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right and on High - SSRF: an authenticated request carrying the app's credentials is driven to an unintended host.

## Target
- File/function: `lib/shopify_api/clients/graphql/client.rb` -> `Clients::Graphql::Client#query`
- Entrypoint: `Graphql::Client#query(query:, variables:, headers:, tries:, response_as_struct:, debug:)`
- Attacker controls: the `debug:` flag, which appends `?debug=true` to the path by string concatenation
- Exploit idea: `"#{@api_version}/graphql.json#{search_params}"` is textual, so a crafted version or flag reshapes the URL
- Invariant to test: AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right
- Expected Immunefi impact: High - SSRF: an authenticated request carrying the app's credentials is driven to an unintended host (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `headers:` cannot override `X-Shopify-Access-Token` in the recorded request
