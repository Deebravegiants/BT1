# Q3567: method_missing — read-only filter applied late via ids hash

## Question
Can the `ids:` hash passed to `base_find`, whose values are interpolated into the request path, supplied by an unprivileged attacker at `method_missing(meth_id, val = nil)`, which turns arbitrary reads and writes into property access, make `Rest::Base#method_missing` and the code consuming its result disagree, given that the read-only filter runs at serialisation time, after values have already been set on the instance? The binding to test is CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted; the impact to prove is High - scope or expiry check bypass granting an operation the session was never authorized for.

## Target
- File/function: `lib/shopify_api/rest/base.rb` -> `Rest::Base#method_missing`
- Entrypoint: `method_missing(meth_id, val = nil)`, which turns arbitrary reads and writes into property access
- Attacker controls: the `ids:` hash passed to `base_find`, whose values are interpolated into the request path
- Exploit idea: the read-only filter runs at serialisation time, after values have already been set on the instance
- Invariant to test: CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted
- Expected Immunefi impact: High - scope or expiry check bypass granting an operation the session was never authorized for (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest + WebMock: call a generated resource's `find` with an `ids` value containing `/` and assert the recorded request path
