# Q357: initialize — version unvalidated here via headers argument

## Question
Can an unprivileged attacker reach `Clients::Graphql::Client#initialize` through `Graphql::Client.new(session:, base_path:, api_version:)` and its version-override branch while supplying the `headers:` argument, which becomes `extra_headers` and is merged over the client defaults, so that the per-client version override is not checked against `SUPPORTED_ADMIN_VERSIONS`, breaking the requirement that CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted, and ending in Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`)?

## Target
- File/function: `lib/shopify_api/clients/graphql/client.rb` -> `Clients::Graphql::Client#initialize`
- Entrypoint: `Graphql::Client.new(session:, base_path:, api_version:)` and its version-override branch
- Attacker controls: the `headers:` argument, which becomes `extra_headers` and is merged over the client defaults
- Exploit idea: the per-client version override is not checked against `SUPPORTED_ADMIN_VERSIONS`
- Invariant to test: CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted
- Expected Immunefi impact: Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`) (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest + WebMock: pass a crafted `api_version` and assert the recorded path stays within the configured version
