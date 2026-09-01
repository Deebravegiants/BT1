# Q1310: query — version unvalidated here via headers argument

## Question
Starting from `Graphql::Client#query(query:, variables:, headers:, tries:, response_as_struct:, debug:)`, can an unprivileged attacker supply the `headers:` argument, which becomes `extra_headers` and is merged over the client defaults so that the per-client version override is not checked against `SUPPORTED_ADMIN_VERSIONS`? Determine whether SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source still holds through `Clients::Graphql::Client#query`, and whether the result reaches High - SSRF: an authenticated request carrying the app's credentials is driven to an unintended host.

## Target
- File/function: `lib/shopify_api/clients/graphql/client.rb` -> `Clients::Graphql::Client#query`
- Entrypoint: `Graphql::Client#query(query:, variables:, headers:, tries:, response_as_struct:, debug:)`
- Attacker controls: the `headers:` argument, which becomes `extra_headers` and is merged over the client defaults
- Exploit idea: the per-client version override is not checked against `SUPPORTED_ADMIN_VERSIONS`
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: High - SSRF: an authenticated request carrying the app's credentials is driven to an unintended host (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert an `OpenStruct`-parsed response cannot define accessors that shadow methods the caller relies on
