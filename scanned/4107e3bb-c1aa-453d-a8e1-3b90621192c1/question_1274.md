# Q1274: initialize — OpenStruct re-parse via headers argument

## Question
Can an unprivileged attacker reach `Clients::Graphql::Client#initialize` through `Graphql::Client.new(session:, base_path:, api_version:)` and its version-override branch while supplying the `headers:` argument, which becomes `extra_headers` and is merged over the client defaults, so that re-parsing response JSON into `OpenStruct` creates dynamically named accessors from response-controlled keys, breaking the requirement that SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source, and ending in High - SSRF: an authenticated request carrying the app's credentials is driven to an unintended host?

## Target
- File/function: `lib/shopify_api/clients/graphql/client.rb` -> `Clients::Graphql::Client#initialize`
- Entrypoint: `Graphql::Client.new(session:, base_path:, api_version:)` and its version-override branch
- Attacker controls: the `headers:` argument, which becomes `extra_headers` and is merged over the client defaults
- Exploit idea: re-parsing response JSON into `OpenStruct` creates dynamically named accessors from response-controlled keys
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: High - SSRF: an authenticated request carrying the app's credentials is driven to an unintended host (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert an `OpenStruct`-parsed response cannot define accessors that shadow methods the caller relies on
