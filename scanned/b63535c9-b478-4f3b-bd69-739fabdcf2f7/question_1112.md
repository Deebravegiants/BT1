# Q1112: query — path built by concatenation via api_version override

## Question
Is there a reachable state in which an unprivileged attacker, controlling an `api_version:` derived from request input, changing the path segment at `Graphql::Client#query(query:, variables:, headers:, tries:, response_as_struct:, debug:)`, makes `Clients::Graphql::Client#query` return a result the caller treats as authenticated, given that `"#{@api_version}/graphql.json#{search_params}"` is textual, so a crafted version or flag reshapes the URL? Test SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source and quantify Critical - cross-tenant access: one shop's request reads or mutates another merchant's data.

## Target
- File/function: `lib/shopify_api/clients/graphql/client.rb` -> `Clients::Graphql::Client#query`
- Entrypoint: `Graphql::Client#query(query:, variables:, headers:, tries:, response_as_struct:, debug:)`
- Attacker controls: an `api_version:` derived from request input, changing the path segment
- Exploit idea: `"#{@api_version}/graphql.json#{search_params}"` is textual, so a crafted version or flag reshapes the URL
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: Critical - cross-tenant access: one shop's request reads or mutates another merchant's data (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert an `OpenStruct`-parsed response cannot define accessors that shadow methods the caller relies on
