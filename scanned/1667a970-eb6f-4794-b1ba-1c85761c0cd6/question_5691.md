# Q5691: save — template selection is textual via session argument

## Question
Can an unprivileged attacker reach `Rest::Base#save` through `save(update_object:)`, which chooses verb and path via `deduce_write_verb` and `deduce_write_path` while supplying the `session:` argument threaded through `base_find` and `save`, which decides whose access token the resource call carries, so that `get_path` picks a template by matching available ids, so a crafted `ids` hash selects a different template than intended, breaking the requirement that CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted, and ending in High - scope or expiry check bypass granting an operation the session was never authorized for?

## Target
- File/function: `lib/shopify_api/rest/base.rb` -> `Rest::Base#save`
- Entrypoint: `save(update_object:)`, which chooses verb and path via `deduce_write_verb` and `deduce_write_path`
- Attacker controls: the `session:` argument threaded through `base_find` and `save`, which decides whose access token the resource call carries
- Exploit idea: `get_path` picks a template by matching available ids, so a crafted `ids` hash selects a different template than intended
- Invariant to test: CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted
- Expected Immunefi impact: High - scope or expiry check bypass granting an operation the session was never authorized for (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest + WebMock: call a generated resource's `find` with an `ids` value containing `/` and assert the recorded request path
