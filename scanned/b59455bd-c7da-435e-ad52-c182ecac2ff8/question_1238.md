# Q1238: initialize — caller headers win via headers argument

## Question
Is there a reachable state in which an unprivileged attacker, controlling the `headers:` argument, which becomes `extra_headers` and is merged over the client defaults at `Graphql::Client.new(session:, base_path:, api_version:)` and its version-override branch, makes `Clients::Graphql::Client#initialize` return a result the caller treats as authenticated, given that `headers:` reaches `extra_headers` and is merged last? Test SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source and quantify High - SSRF: an authenticated request carrying the app's credentials is driven to an unintended host.

## Target
- File/function: `lib/shopify_api/clients/graphql/client.rb` -> `Clients::Graphql::Client#initialize`
- Entrypoint: `Graphql::Client.new(session:, base_path:, api_version:)` and its version-override branch
- Attacker controls: the `headers:` argument, which becomes `extra_headers` and is merged over the client defaults
- Exploit idea: `headers:` reaches `extra_headers` and is merged last
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: High - SSRF: an authenticated request carrying the app's credentials is driven to an unintended host (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert an `OpenStruct`-parsed response cannot define accessors that shadow methods the caller relies on
