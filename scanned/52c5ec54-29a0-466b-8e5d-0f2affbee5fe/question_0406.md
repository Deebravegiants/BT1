# Q406: initialize — caller headers win via query document

## Question
Can an unprivileged attacker reach `Clients::Graphql::Client#initialize` through `Graphql::Client.new(session:, base_path:, api_version:)` and its version-override branch while supplying the GraphQL document, forwarded verbatim with the merchant's access token attached, so that `headers:` reaches `extra_headers` and is merged last, breaking the requirement that AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right, and ending in High - SSRF: an authenticated request carrying the app's credentials is driven to an unintended host?

## Target
- File/function: `lib/shopify_api/clients/graphql/client.rb` -> `Clients::Graphql::Client#initialize`
- Entrypoint: `Graphql::Client.new(session:, base_path:, api_version:)` and its version-override branch
- Attacker controls: the GraphQL document, forwarded verbatim with the merchant's access token attached
- Exploit idea: `headers:` reaches `extra_headers` and is merged last
- Invariant to test: AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right
- Expected Immunefi impact: High - SSRF: an authenticated request carrying the app's credentials is driven to an unintended host (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `headers:` cannot override `X-Shopify-Access-Token` in the recorded request
