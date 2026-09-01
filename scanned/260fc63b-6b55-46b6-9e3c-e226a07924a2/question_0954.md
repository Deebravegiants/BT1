# Q954: initialize — OpenStruct re-parse via debug flag

## Question
Does `Clients::Graphql::Client#initialize` collapse two distinct identities into one when an unprivileged attacker submits the `debug:` flag, which appends `?debug=true` to the path by string concatenation at `Graphql::Client.new(session:, base_path:, api_version:)` and its version-override branch? Show that re-parsing response JSON into `OpenStruct` creates dynamically named accessors from response-controlled keys, that CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted is violated, and that the consequence is High - SSRF: an authenticated request carrying the app's credentials is driven to an unintended host.

## Target
- File/function: `lib/shopify_api/clients/graphql/client.rb` -> `Clients::Graphql::Client#initialize`
- Entrypoint: `Graphql::Client.new(session:, base_path:, api_version:)` and its version-override branch
- Attacker controls: the `debug:` flag, which appends `?debug=true` to the path by string concatenation
- Exploit idea: re-parsing response JSON into `OpenStruct` creates dynamically named accessors from response-controlled keys
- Invariant to test: CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted
- Expected Immunefi impact: High - SSRF: an authenticated request carrying the app's credentials is driven to an unintended host (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest + WebMock: pass a crafted `api_version` and assert the recorded path stays within the configured version
