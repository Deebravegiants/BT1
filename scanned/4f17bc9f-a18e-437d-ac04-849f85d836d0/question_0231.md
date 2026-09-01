# Q231: query — no operation policy via api_version override

## Question
Can an unprivileged attacker reach `Clients::Graphql::Client#query` through `Graphql::Client#query(query:, variables:, headers:, tries:, response_as_struct:, debug:)` while supplying an `api_version:` derived from request input, changing the path segment, so that no distinction between queries and mutations, and no scope check against the session, breaking the requirement that CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted, and ending in High - scope or expiry check bypass granting an operation the session was never authorized for?

## Target
- File/function: `lib/shopify_api/clients/graphql/client.rb` -> `Clients::Graphql::Client#query`
- Entrypoint: `Graphql::Client#query(query:, variables:, headers:, tries:, response_as_struct:, debug:)`
- Attacker controls: an `api_version:` derived from request input, changing the path segment
- Exploit idea: no distinction between queries and mutations, and no scope check against the session
- Invariant to test: CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted
- Expected Immunefi impact: High - scope or expiry check bypass granting an operation the session was never authorized for (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest + WebMock: pass a crafted `api_version` and assert the recorded path stays within the configured version
