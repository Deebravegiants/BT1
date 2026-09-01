# Q1323: set_property — read-only filter applied late via session argument

## Question
Can an unprivileged attacker reach `Rest::Base#set_property` through `set_property(key, val)`, which performs `instance_variable_set("@#{clean_key}", val)` with a key taken from response data while supplying the `session:` argument threaded through `base_find` and `save`, which decides whose access token the resource call carries, so that the read-only filter runs at serialisation time, after values have already been set on the instance, breaking the requirement that CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted, and ending in High - scope or expiry check bypass granting an operation the session was never authorized for?

## Target
- File/function: `lib/shopify_api/rest/base.rb` -> `Rest::Base#set_property`
- Entrypoint: `set_property(key, val)`, which performs `instance_variable_set("@#{clean_key}", val)` with a key taken from response data
- Attacker controls: the `session:` argument threaded through `base_find` and `save`, which decides whose access token the resource call carries
- Exploit idea: the read-only filter runs at serialisation time, after values have already been set on the instance
- Invariant to test: CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted
- Expected Immunefi impact: High - scope or expiry check bypass granting an operation the session was never authorized for (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest + WebMock: call a generated resource's `find` with an `ids` value containing `/` and assert the recorded request path
