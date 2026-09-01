# Q4803: save — read-only filter applied late via has_many element class

## Question
Starting from `save(update_object:)`, which chooses verb and path via `deduce_write_verb` and `deduce_write_path`, can an unprivileged attacker supply the element class resolved for a `has_many` attribute from response data, which decides how nested payloads are instantiated so that the read-only filter runs at serialisation time, after values have already been set on the instance? Determine whether CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted still holds through `Rest::Base#save`, and whether the result reaches High - scope or expiry check bypass granting an operation the session was never authorized for.

## Target
- File/function: `lib/shopify_api/rest/base.rb` -> `Rest::Base#save`
- Entrypoint: `save(update_object:)`, which chooses verb and path via `deduce_write_verb` and `deduce_write_path`
- Attacker controls: the element class resolved for a `has_many` attribute from response data, which decides how nested payloads are instantiated
- Exploit idea: the read-only filter runs at serialisation time, after values have already been set on the instance
- Invariant to test: CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted
- Expected Immunefi impact: High - scope or expiry check bypass granting an operation the session was never authorized for (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest + WebMock: call a generated resource's `find` with an `ids` value containing `/` and assert the recorded request path
