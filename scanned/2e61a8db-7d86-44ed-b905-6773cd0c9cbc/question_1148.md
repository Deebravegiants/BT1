# Q1148: initialize — caller headers win via response_as_struct

## Question
Can an unprivileged attacker reach `Clients::Graphql::Client#initialize` through `Graphql::Client.new(session:, base_path:, api_version:)` and its version-override branch while supplying the `response_as_struct` flag, which re-parses the body into `OpenStruct` objects, so that `headers:` reaches `extra_headers` and is merged last, breaking the requirement that SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source, and ending in Critical - cross-tenant access: one shop's request reads or mutates another merchant's data?

## Target
- File/function: `lib/shopify_api/clients/graphql/client.rb` -> `Clients::Graphql::Client#initialize`
- Entrypoint: `Graphql::Client.new(session:, base_path:, api_version:)` and its version-override branch
- Attacker controls: the `response_as_struct` flag, which re-parses the body into `OpenStruct` objects
- Exploit idea: `headers:` reaches `extra_headers` and is merged last
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: Critical - cross-tenant access: one shop's request reads or mutates another merchant's data (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert an `OpenStruct`-parsed response cannot define accessors that shadow methods the caller relies on
