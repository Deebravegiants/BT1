# Q5268: set_property — cursor trusted via read-only attribute

## Question
Can an attribute listed in `read_only_attributes` presented in a payload that reaches `attributes_to_update`, supplied by an unprivileged attacker at `set_property(key, val)`, which performs `instance_variable_set("@#{clean_key}", val)` with a key taken from response data, make `Rest::Base#set_property` and the code consuming its result disagree, given that page-info cursors from a response are replayed into the next authenticated request without validation? The binding to test is CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted; the impact to prove is Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`).

## Target
- File/function: `lib/shopify_api/rest/base.rb` -> `Rest::Base#set_property`
- Entrypoint: `set_property(key, val)`, which performs `instance_variable_set("@#{clean_key}", val)` with a key taken from response data
- Attacker controls: an attribute listed in `read_only_attributes` presented in a payload that reaches `attributes_to_update`
- Exploit idea: page-info cursors from a response are replayed into the next authenticated request without validation
- Invariant to test: CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted
- Expected Immunefi impact: Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`) (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest + WebMock: call a generated resource's `find` with an `ids` value containing `/` and assert the recorded request path
