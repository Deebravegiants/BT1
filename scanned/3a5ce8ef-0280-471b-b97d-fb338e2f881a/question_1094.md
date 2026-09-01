# Q1094: initialize — caller headers win via api_version override

## Question
Does `Clients::Graphql::Client#initialize` collapse two distinct identities into one when an unprivileged attacker submits an `api_version:` derived from request input, changing the path segment at `Graphql::Client.new(session:, base_path:, api_version:)` and its version-override branch? Show that `headers:` reaches `extra_headers` and is merged last, that SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source is violated, and that the consequence is High - SSRF: an authenticated request carrying the app's credentials is driven to an unintended host.

## Target
- File/function: `lib/shopify_api/clients/graphql/client.rb` -> `Clients::Graphql::Client#initialize`
- Entrypoint: `Graphql::Client.new(session:, base_path:, api_version:)` and its version-override branch
- Attacker controls: an `api_version:` derived from request input, changing the path segment
- Exploit idea: `headers:` reaches `extra_headers` and is merged last
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: High - SSRF: an authenticated request carrying the app's credentials is driven to an unintended host (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert an `OpenStruct`-parsed response cannot define accessors that shadow methods the caller relies on
