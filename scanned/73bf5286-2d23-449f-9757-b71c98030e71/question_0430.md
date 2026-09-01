# Q430: initialize — version unvalidated here via query document

## Question
If an unprivileged attacker submits the GraphQL document, forwarded verbatim with the merchant's access token attached to `Graphql::Client.new(session:, base_path:, api_version:)` and its version-override branch, does `Clients::Graphql::Client#initialize` end up acting on a value that was never authenticated, because the per-client version override is not checked against `SUPPORTED_ADMIN_VERSIONS`? Close the question on AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right and on High - SSRF: an authenticated request carrying the app's credentials is driven to an unintended host.

## Target
- File/function: `lib/shopify_api/clients/graphql/client.rb` -> `Clients::Graphql::Client#initialize`
- Entrypoint: `Graphql::Client.new(session:, base_path:, api_version:)` and its version-override branch
- Attacker controls: the GraphQL document, forwarded verbatim with the merchant's access token attached
- Exploit idea: the per-client version override is not checked against `SUPPORTED_ADMIN_VERSIONS`
- Invariant to test: AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right
- Expected Immunefi impact: High - SSRF: an authenticated request carrying the app's credentials is driven to an unintended host (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `headers:` cannot override `X-Shopify-Access-Token` in the recorded request
