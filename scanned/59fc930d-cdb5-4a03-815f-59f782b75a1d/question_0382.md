# Q382: initialize — caller headers win via debug flag

## Question
Can the `debug:` flag, which appends `?debug=true` to the path by string concatenation, supplied by an unprivileged attacker at `Graphql::Client.new(session:, base_path:, api_version:)` and its version-override branch, make `Clients::Graphql::Client#initialize` and the code consuming its result disagree, given that `headers:` reaches `extra_headers` and is merged last? The binding to test is AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right; the impact to prove is High - SSRF: an authenticated request carrying the app's credentials is driven to an unintended host.

## Target
- File/function: `lib/shopify_api/clients/graphql/client.rb` -> `Clients::Graphql::Client#initialize`
- Entrypoint: `Graphql::Client.new(session:, base_path:, api_version:)` and its version-override branch
- Attacker controls: the `debug:` flag, which appends `?debug=true` to the path by string concatenation
- Exploit idea: `headers:` reaches `extra_headers` and is merged last
- Invariant to test: AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right
- Expected Immunefi impact: High - SSRF: an authenticated request carrying the app's credentials is driven to an unintended host (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `headers:` cannot override `X-Shopify-Access-Token` in the recorded request
