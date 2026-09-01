# Q1233: to_hash — read-only filter applied late via params hash

## Question
Starting from `to_hash(saving)`, which walks `instance_variables` and filters `read_only_attributes`, can an unprivileged attacker supply the `params:` hash, forwarded as the outgoing query string so that the read-only filter runs at serialisation time, after values have already been set on the instance? Determine whether CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted still holds through `Rest::Base#to_hash`, and whether the result reaches High - SSRF: an authenticated request carrying the app's credentials is driven to an unintended host.

## Target
- File/function: `lib/shopify_api/rest/base.rb` -> `Rest::Base#to_hash`
- Entrypoint: `to_hash(saving)`, which walks `instance_variables` and filters `read_only_attributes`
- Attacker controls: the `params:` hash, forwarded as the outgoing query string
- Exploit idea: the read-only filter runs at serialisation time, after values have already been set on the instance
- Invariant to test: CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted
- Expected Immunefi impact: High - SSRF: an authenticated request carrying the app's credentials is driven to an unintended host (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest + WebMock: call a generated resource's `find` with an `ids` value containing `/` and assert the recorded request path
