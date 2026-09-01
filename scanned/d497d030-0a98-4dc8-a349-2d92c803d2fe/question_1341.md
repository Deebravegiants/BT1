# Q1341: build_check_query — GraphQL by interpolation via topic string

## Question
Can the `@topic` value interpolated into `build_check_query` unquoted, supplied by an unprivileged attacker at `build_check_query`, which interpolates `@topic` into a GraphQL document, make `Registrations::Http#build_check_query` and the code consuming its result disagree, given that topic and argument strings are concatenated into the document rather than passed as variables? The binding to test is CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted; the impact to prove is High - SSRF: an authenticated request carrying the app's credentials is driven to an unintended host.

## Target
- File/function: `lib/shopify_api/webhooks/registrations/http.rb` -> `Registrations::Http#build_check_query`
- Entrypoint: `build_check_query`, which interpolates `@topic` into a GraphQL document
- Attacker controls: the `@topic` value interpolated into `build_check_query` unquoted
- Exploit idea: topic and argument strings are concatenated into the document rather than passed as variables
- Invariant to test: CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted
- Expected Immunefi impact: High - SSRF: an authenticated request carrying the app's credentials is driven to an unintended host (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest: set `Context.host_name` and assert `callback_address` rejects a path whose prefix merely matches it
