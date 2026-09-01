# Q1166: initialize — no operation policy via api_version override

## Question
Can an `api_version:` derived from request input, changing the path segment, supplied by an unprivileged attacker at `Graphql::Client.new(session:, base_path:, api_version:)` and its version-override branch, make `Clients::Graphql::Client#initialize` and the code consuming its result disagree, given that no distinction between queries and mutations, and no scope check against the session? The binding to test is SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source; the impact to prove is High - SSRF: an authenticated request carrying the app's credentials is driven to an unintended host.

## Target
- File/function: `lib/shopify_api/clients/graphql/client.rb` -> `Clients::Graphql::Client#initialize`
- Entrypoint: `Graphql::Client.new(session:, base_path:, api_version:)` and its version-override branch
- Attacker controls: an `api_version:` derived from request input, changing the path segment
- Exploit idea: no distinction between queries and mutations, and no scope check against the session
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: High - SSRF: an authenticated request carrying the app's credentials is driven to an unintended host (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert an `OpenStruct`-parsed response cannot define accessors that shadow methods the caller relies on
