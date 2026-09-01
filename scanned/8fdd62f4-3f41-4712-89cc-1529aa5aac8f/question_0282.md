# Q282: query — OpenStruct re-parse via query document

## Question
Does `Clients::Graphql::Client#query` collapse two distinct identities into one when an unprivileged attacker submits the GraphQL document, forwarded verbatim with the merchant's access token attached at `Graphql::Client#query(query:, variables:, headers:, tries:, response_as_struct:, debug:)`? Show that re-parsing response JSON into `OpenStruct` creates dynamically named accessors from response-controlled keys, that CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted is violated, and that the consequence is High - SSRF: an authenticated request carrying the app's credentials is driven to an unintended host.

## Target
- File/function: `lib/shopify_api/clients/graphql/client.rb` -> `Clients::Graphql::Client#query`
- Entrypoint: `Graphql::Client#query(query:, variables:, headers:, tries:, response_as_struct:, debug:)`
- Attacker controls: the GraphQL document, forwarded verbatim with the merchant's access token attached
- Exploit idea: re-parsing response JSON into `OpenStruct` creates dynamically named accessors from response-controlled keys
- Invariant to test: CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted
- Expected Immunefi impact: High - SSRF: an authenticated request carrying the app's credentials is driven to an unintended host (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest + WebMock: pass a crafted `api_version` and assert the recorded path stays within the configured version
