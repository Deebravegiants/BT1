# Q5760: method_missing — query forwarded verbatim via nested has_many/has_one

## Question
Is there a reachable state in which an unprivileged attacker, controlling nested objects whose class is resolved from the attribute name at `method_missing(meth_id, val = nil)`, which turns arbitrary reads and writes into property access, makes `Rest::Base#method_missing` return a result the caller treats as authenticated, given that `params:` is passed through to the outgoing query with the merchant's token attached? Test CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted and quantify Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`).

## Target
- File/function: `lib/shopify_api/rest/base.rb` -> `Rest::Base#method_missing`
- Entrypoint: `method_missing(meth_id, val = nil)`, which turns arbitrary reads and writes into property access
- Attacker controls: nested objects whose class is resolved from the attribute name
- Exploit idea: `params:` is passed through to the outgoing query with the merchant's token attached
- Invariant to test: CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted
- Expected Immunefi impact: Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`) (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest + WebMock: call a generated resource's `find` with an `ids` value containing `/` and assert the recorded request path
