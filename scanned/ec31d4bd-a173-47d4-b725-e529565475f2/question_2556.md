# Q2556: base_find — dynamic dispatch on response data via has_many element class

## Question
Starting from `base_find(session:, ids:, params:)`, called by every generated `find`/`all` with caller-supplied `ids` and `params`, can an unprivileged attacker supply the element class resolved for a `has_many` attribute from response data, which decides how nested payloads are instantiated so that `public_send` and `instance_variable_set` targets are derived from data returned by the upstream call, not from a fixed allow-list? Determine whether CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted still holds through `Rest::Base.base_find`, and whether the result reaches Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`).

## Target
- File/function: `lib/shopify_api/rest/base.rb` -> `Rest::Base.base_find`
- Entrypoint: `base_find(session:, ids:, params:)`, called by every generated `find`/`all` with caller-supplied `ids` and `params`
- Attacker controls: the element class resolved for a `has_many` attribute from response data, which decides how nested payloads are instantiated
- Exploit idea: `public_send` and `instance_variable_set` targets are derived from data returned by the upstream call, not from a fixed allow-list
- Invariant to test: CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted
- Expected Immunefi impact: Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`) (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest + WebMock: call a generated resource's `find` with an `ids` value containing `/` and assert the recorded request path
