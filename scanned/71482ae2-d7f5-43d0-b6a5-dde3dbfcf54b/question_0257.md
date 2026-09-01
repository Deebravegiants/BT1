# Q257: query — no operation policy via debug flag

## Question
Trace `Clients::Graphql::Client#query` from `Graphql::Client#query(query:, variables:, headers:, tries:, response_as_struct:, debug:)` with the `debug:` flag, which appends `?debug=true` to the path by string concatenation: because no distinction between queries and mutations, and no scope check against the session, does the value that was verified stop being the value that is used? Prove the break against SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source and map it to Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`).

## Target
- File/function: `lib/shopify_api/clients/graphql/client.rb` -> `Clients::Graphql::Client#query`
- Entrypoint: `Graphql::Client#query(query:, variables:, headers:, tries:, response_as_struct:, debug:)`
- Attacker controls: the `debug:` flag, which appends `?debug=true` to the path by string concatenation
- Exploit idea: no distinction between queries and mutations, and no scope check against the session
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`) (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert an `OpenStruct`-parsed response cannot define accessors that shadow methods the caller relies on
