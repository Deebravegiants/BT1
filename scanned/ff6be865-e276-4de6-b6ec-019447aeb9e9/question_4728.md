# Q4728: create_instance — cursor trusted via read-only attribute

## Question
If an unprivileged attacker submits an attribute listed in `read_only_attributes` presented in a payload that reaches `attributes_to_update` to `create_instance(data:, session:, instance:)`, which builds objects from API response JSON via `public_send("#{attribute}=", ...)`, does `Rest::Base.create_instance` end up acting on a value that was never authenticated, because page-info cursors from a response are replayed into the next authenticated request without validation? Close the question on CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted and on Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`).

## Target
- File/function: `lib/shopify_api/rest/base.rb` -> `Rest::Base.create_instance`
- Entrypoint: `create_instance(data:, session:, instance:)`, which builds objects from API response JSON via `public_send("#{attribute}=", ...)`
- Attacker controls: an attribute listed in `read_only_attributes` presented in a payload that reaches `attributes_to_update`
- Exploit idea: page-info cursors from a response are replayed into the next authenticated request without validation
- Invariant to test: CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted
- Expected Immunefi impact: Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`) (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest + WebMock: call a generated resource's `find` with an `ids` value containing `/` and assert the recorded request path
