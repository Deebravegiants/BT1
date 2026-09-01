# Q75: query — OpenStruct re-parse via headers argument

## Question
Trace `Clients::Graphql::Client#query` from `Graphql::Client#query(query:, variables:, headers:, tries:, response_as_struct:, debug:)` with the `headers:` argument, which becomes `extra_headers` and is merged over the client defaults: because re-parsing response JSON into `OpenStruct` creates dynamically named accessors from response-controlled keys, does the value that was verified stop being the value that is used? Prove the break against CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted and map it to High - scope or expiry check bypass granting an operation the session was never authorized for.

## Target
- File/function: `lib/shopify_api/clients/graphql/client.rb` -> `Clients::Graphql::Client#query`
- Entrypoint: `Graphql::Client#query(query:, variables:, headers:, tries:, response_as_struct:, debug:)`
- Attacker controls: the `headers:` argument, which becomes `extra_headers` and is merged over the client defaults
- Exploit idea: re-parsing response JSON into `OpenStruct` creates dynamically named accessors from response-controlled keys
- Invariant to test: CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted
- Expected Immunefi impact: High - scope or expiry check bypass granting an operation the session was never authorized for (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest + WebMock: pass a crafted `api_version` and assert the recorded path stays within the configured version
