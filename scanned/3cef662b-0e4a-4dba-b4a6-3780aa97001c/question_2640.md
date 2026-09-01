# Q2640: method_missing — template selection is textual via pagination cursors

## Question
Starting from `method_missing(meth_id, val = nil)`, which turns arbitrary reads and writes into property access, can an unprivileged attacker supply `prev_page_info` / `next_page_info` values taken from response `Link` headers and replayed into a subsequent request so that `get_path` picks a template by matching available ids, so a crafted `ids` hash selects a different template than intended? Determine whether CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted still holds through `Rest::Base#method_missing`, and whether the result reaches Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`).

## Target
- File/function: `lib/shopify_api/rest/base.rb` -> `Rest::Base#method_missing`
- Entrypoint: `method_missing(meth_id, val = nil)`, which turns arbitrary reads and writes into property access
- Attacker controls: `prev_page_info` / `next_page_info` values taken from response `Link` headers and replayed into a subsequent request
- Exploit idea: `get_path` picks a template by matching available ids, so a crafted `ids` hash selects a different template than intended
- Invariant to test: CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted
- Expected Immunefi impact: Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`) (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest + WebMock: call a generated resource's `find` with an `ids` value containing `/` and assert the recorded request path
