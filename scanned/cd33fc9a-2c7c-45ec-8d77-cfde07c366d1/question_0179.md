# Q179: query — caller headers win via api_version override

## Question
Can an `api_version:` derived from request input, changing the path segment, supplied by an unprivileged attacker at `Graphql::Client#query(query:, variables:, headers:, tries:, response_as_struct:, debug:)`, make `Clients::Graphql::Client#query` and the code consuming its result disagree, given that `headers:` reaches `extra_headers` and is merged last? The binding to test is SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source; the impact to prove is High - scope or expiry check bypass granting an operation the session was never authorized for.

## Target
- File/function: `lib/shopify_api/clients/graphql/client.rb` -> `Clients::Graphql::Client#query`
- Entrypoint: `Graphql::Client#query(query:, variables:, headers:, tries:, response_as_struct:, debug:)`
- Attacker controls: an `api_version:` derived from request input, changing the path segment
- Exploit idea: `headers:` reaches `extra_headers` and is merged last
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: High - scope or expiry check bypass granting an operation the session was never authorized for (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert an `OpenStruct`-parsed response cannot define accessors that shadow methods the caller relies on
