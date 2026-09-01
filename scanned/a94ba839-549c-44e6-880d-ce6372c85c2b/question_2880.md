# Q2880: to_hash — dynamic dispatch on response data via pagination cursors

## Question
If an unprivileged attacker submits `prev_page_info` / `next_page_info` values taken from response `Link` headers and replayed into a subsequent request to `to_hash(saving)`, which walks `instance_variables` and filters `read_only_attributes`, does `Rest::Base#to_hash` end up acting on a value that was never authenticated, because `public_send` and `instance_variable_set` targets are derived from data returned by the upstream call, not from a fixed allow-list? Close the question on CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted and on Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`).

## Target
- File/function: `lib/shopify_api/rest/base.rb` -> `Rest::Base#to_hash`
- Entrypoint: `to_hash(saving)`, which walks `instance_variables` and filters `read_only_attributes`
- Attacker controls: `prev_page_info` / `next_page_info` values taken from response `Link` headers and replayed into a subsequent request
- Exploit idea: `public_send` and `instance_variable_set` targets are derived from data returned by the upstream call, not from a fixed allow-list
- Invariant to test: CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted
- Expected Immunefi impact: Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`) (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest + WebMock: call a generated resource's `find` with an `ids` value containing `/` and assert the recorded request path
