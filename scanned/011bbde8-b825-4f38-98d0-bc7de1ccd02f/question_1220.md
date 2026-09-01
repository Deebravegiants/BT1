# Q1220: query — no operation policy via response_as_struct

## Question
Does `Clients::Graphql::Client#query` collapse two distinct identities into one when an unprivileged attacker submits the `response_as_struct` flag, which re-parses the body into `OpenStruct` objects at `Graphql::Client#query(query:, variables:, headers:, tries:, response_as_struct:, debug:)`? Show that no distinction between queries and mutations, and no scope check against the session, that SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source is violated, and that the consequence is Critical - cross-tenant access: one shop's request reads or mutates another merchant's data.

## Target
- File/function: `lib/shopify_api/clients/graphql/client.rb` -> `Clients::Graphql::Client#query`
- Entrypoint: `Graphql::Client#query(query:, variables:, headers:, tries:, response_as_struct:, debug:)`
- Attacker controls: the `response_as_struct` flag, which re-parses the body into `OpenStruct` objects
- Exploit idea: no distinction between queries and mutations, and no scope check against the session
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: Critical - cross-tenant access: one shop's request reads or mutates another merchant's data (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert an `OpenStruct`-parsed response cannot define accessors that shadow methods the caller relies on
