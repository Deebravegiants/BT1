# Q4563: to_hash — template selection is textual via session argument

## Question
Is there a reachable state in which an unprivileged attacker, controlling the `session:` argument threaded through `base_find` and `save`, which decides whose access token the resource call carries at `to_hash(saving)`, which walks `instance_variables` and filters `read_only_attributes`, makes `Rest::Base#to_hash` return a result the caller treats as authenticated, given that `get_path` picks a template by matching available ids, so a crafted `ids` hash selects a different template than intended? Test CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted and quantify High - scope or expiry check bypass granting an operation the session was never authorized for.

## Target
- File/function: `lib/shopify_api/rest/base.rb` -> `Rest::Base#to_hash`
- Entrypoint: `to_hash(saving)`, which walks `instance_variables` and filters `read_only_attributes`
- Attacker controls: the `session:` argument threaded through `base_find` and `save`, which decides whose access token the resource call carries
- Exploit idea: `get_path` picks a template by matching available ids, so a crafted `ids` hash selects a different template than intended
- Invariant to test: CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted
- Expected Immunefi impact: High - scope or expiry check bypass granting an operation the session was never authorized for (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest + WebMock: call a generated resource's `find` with an `ids` value containing `/` and assert the recorded request path
