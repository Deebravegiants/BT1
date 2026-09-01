# Q1130: initialize — no operation policy via query document

## Question
If an unprivileged attacker submits the GraphQL document, forwarded verbatim with the merchant's access token attached to `Graphql::Client.new(session:, base_path:, api_version:)` and its version-override branch, does `Clients::Graphql::Client#initialize` end up acting on a value that was never authenticated, because no distinction between queries and mutations, and no scope check against the session? Close the question on SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source and on High - SSRF: an authenticated request carrying the app's credentials is driven to an unintended host.

## Target
- File/function: `lib/shopify_api/clients/graphql/client.rb` -> `Clients::Graphql::Client#initialize`
- Entrypoint: `Graphql::Client.new(session:, base_path:, api_version:)` and its version-override branch
- Attacker controls: the GraphQL document, forwarded verbatim with the merchant's access token attached
- Exploit idea: no distinction between queries and mutations, and no scope check against the session
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: High - SSRF: an authenticated request carrying the app's credentials is driven to an unintended host (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert an `OpenStruct`-parsed response cannot define accessors that shadow methods the caller relies on
