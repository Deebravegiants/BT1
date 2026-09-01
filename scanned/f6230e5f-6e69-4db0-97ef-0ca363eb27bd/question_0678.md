# Q678: query — version unvalidated here via variables hash

## Question
Is there a reachable state in which an unprivileged attacker, controlling the `variables` hash, serialised into the request body at `Graphql::Client#query(query:, variables:, headers:, tries:, response_as_struct:, debug:)`, makes `Clients::Graphql::Client#query` return a result the caller treats as authenticated, given that the per-client version override is not checked against `SUPPORTED_ADMIN_VERSIONS`? Test CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted and quantify High - SSRF: an authenticated request carrying the app's credentials is driven to an unintended host.

## Target
- File/function: `lib/shopify_api/clients/graphql/client.rb` -> `Clients::Graphql::Client#query`
- Entrypoint: `Graphql::Client#query(query:, variables:, headers:, tries:, response_as_struct:, debug:)`
- Attacker controls: the `variables` hash, serialised into the request body
- Exploit idea: the per-client version override is not checked against `SUPPORTED_ADMIN_VERSIONS`
- Invariant to test: CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted
- Expected Immunefi impact: High - SSRF: an authenticated request carrying the app's credentials is driven to an unintended host (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest + WebMock: pass a crafted `api_version` and assert the recorded path stays within the configured version
