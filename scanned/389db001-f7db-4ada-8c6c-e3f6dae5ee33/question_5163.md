# Q5163: save — query forwarded verbatim via read-only attribute

## Question
Can an attribute listed in `read_only_attributes` presented in a payload that reaches `attributes_to_update`, supplied by an unprivileged attacker at `save(update_object:)`, which chooses verb and path via `deduce_write_verb` and `deduce_write_path`, make `Rest::Base#save` and the code consuming its result disagree, given that `params:` is passed through to the outgoing query with the merchant's token attached? The binding to test is CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted; the impact to prove is High - scope or expiry check bypass granting an operation the session was never authorized for.

## Target
- File/function: `lib/shopify_api/rest/base.rb` -> `Rest::Base#save`
- Entrypoint: `save(update_object:)`, which chooses verb and path via `deduce_write_verb` and `deduce_write_path`
- Attacker controls: an attribute listed in `read_only_attributes` presented in a payload that reaches `attributes_to_update`
- Exploit idea: `params:` is passed through to the outgoing query with the merchant's token attached
- Invariant to test: CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted
- Expected Immunefi impact: High - scope or expiry check bypass granting an operation the session was never authorized for (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest + WebMock: call a generated resource's `find` with an `ids` value containing `/` and assert the recorded request path
