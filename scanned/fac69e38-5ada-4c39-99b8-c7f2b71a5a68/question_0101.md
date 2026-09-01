# Q101: initialize — version unvalidated here via api_version override

## Question
If an unprivileged attacker submits an `api_version:` derived from request input, changing the path segment to `Graphql::Client.new(session:, base_path:, api_version:)` and its version-override branch, does `Clients::Graphql::Client#initialize` end up acting on a value that was never authenticated, because the per-client version override is not checked against `SUPPORTED_ADMIN_VERSIONS`? Close the question on SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source and on Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`).

## Target
- File/function: `lib/shopify_api/clients/graphql/client.rb` -> `Clients::Graphql::Client#initialize`
- Entrypoint: `Graphql::Client.new(session:, base_path:, api_version:)` and its version-override branch
- Attacker controls: an `api_version:` derived from request input, changing the path segment
- Exploit idea: the per-client version override is not checked against `SUPPORTED_ADMIN_VERSIONS`
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`) (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert an `OpenStruct`-parsed response cannot define accessors that shadow methods the caller relies on
