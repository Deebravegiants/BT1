# Q1256: initialize — path built by concatenation via debug flag

## Question
If an unprivileged attacker submits the `debug:` flag, which appends `?debug=true` to the path by string concatenation to `Graphql::Client.new(session:, base_path:, api_version:)` and its version-override branch, does `Clients::Graphql::Client#initialize` end up acting on a value that was never authenticated, because `"#{@api_version}/graphql.json#{search_params}"` is textual, so a crafted version or flag reshapes the URL? Close the question on SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source and on Critical - cross-tenant access: one shop's request reads or mutates another merchant's data.

## Target
- File/function: `lib/shopify_api/clients/graphql/client.rb` -> `Clients::Graphql::Client#initialize`
- Entrypoint: `Graphql::Client.new(session:, base_path:, api_version:)` and its version-override branch
- Attacker controls: the `debug:` flag, which appends `?debug=true` to the path by string concatenation
- Exploit idea: `"#{@api_version}/graphql.json#{search_params}"` is textual, so a crafted version or flag reshapes the URL
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: Critical - cross-tenant access: one shop's request reads or mutates another merchant's data (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert an `OpenStruct`-parsed response cannot define accessors that shadow methods the caller relies on
