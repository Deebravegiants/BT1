# Q974: initialize — path built by concatenation via headers argument

## Question
Starting from `Graphql::Client.new(session:, base_path:, api_version:)` and its version-override branch, can an unprivileged attacker supply the `headers:` argument, which becomes `extra_headers` and is merged over the client defaults so that `"#{@api_version}/graphql.json#{search_params}"` is textual, so a crafted version or flag reshapes the URL? Determine whether SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source still holds through `Clients::Graphql::Client#initialize`, and whether the result reaches High - SSRF: an authenticated request carrying the app's credentials is driven to an unintended host.

## Target
- File/function: `lib/shopify_api/clients/graphql/client.rb` -> `Clients::Graphql::Client#initialize`
- Entrypoint: `Graphql::Client.new(session:, base_path:, api_version:)` and its version-override branch
- Attacker controls: the `headers:` argument, which becomes `extra_headers` and is merged over the client defaults
- Exploit idea: `"#{@api_version}/graphql.json#{search_params}"` is textual, so a crafted version or flag reshapes the URL
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: High - SSRF: an authenticated request carrying the app's credentials is driven to an unintended host (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert an `OpenStruct`-parsed response cannot define accessors that shadow methods the caller relies on
