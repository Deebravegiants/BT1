# Q1215: set_property — method shadowing via attribute shadowing a method

## Question
Can a response key that collides with an existing method such as `session`, `client`, `id` or `original_state`, supplied by an unprivileged attacker at `set_property(key, val)`, which performs `instance_variable_set("@#{clean_key}", val)` with a key taken from response data, make `Rest::Base#set_property` and the code consuming its result disagree, given that a property write can shadow or overwrite internal state such as the session or client held on the instance? The binding to test is CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted; the impact to prove is High - scope or expiry check bypass granting an operation the session was never authorized for.

## Target
- File/function: `lib/shopify_api/rest/base.rb` -> `Rest::Base#set_property`
- Entrypoint: `set_property(key, val)`, which performs `instance_variable_set("@#{clean_key}", val)` with a key taken from response data
- Attacker controls: a response key that collides with an existing method such as `session`, `client`, `id` or `original_state`
- Exploit idea: a property write can shadow or overwrite internal state such as the session or client held on the instance
- Invariant to test: CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted
- Expected Immunefi impact: High - scope or expiry check bypass granting an operation the session was never authorized for (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest + WebMock: call a generated resource's `find` with an `ids` value containing `/` and assert the recorded request path
