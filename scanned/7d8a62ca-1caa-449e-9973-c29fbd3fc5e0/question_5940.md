# Q5940: save — template selection is textual via pagination cursors

## Question
Can `prev_page_info` / `next_page_info` values taken from response `Link` headers and replayed into a subsequent request, supplied by an unprivileged attacker at `save(update_object:)`, which chooses verb and path via `deduce_write_verb` and `deduce_write_path`, make `Rest::Base#save` and the code consuming its result disagree, given that `get_path` picks a template by matching available ids, so a crafted `ids` hash selects a different template than intended? The binding to test is CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted; the impact to prove is Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`).

## Target
- File/function: `lib/shopify_api/rest/base.rb` -> `Rest::Base#save`
- Entrypoint: `save(update_object:)`, which chooses verb and path via `deduce_write_verb` and `deduce_write_path`
- Attacker controls: `prev_page_info` / `next_page_info` values taken from response `Link` headers and replayed into a subsequent request
- Exploit idea: `get_path` picks a template by matching available ids, so a crafted `ids` hash selects a different template than intended
- Invariant to test: CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted
- Expected Immunefi impact: Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`) (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest + WebMock: call a generated resource's `find` with an `ids` value containing `/` and assert the recorded request path
