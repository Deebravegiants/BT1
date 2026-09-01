# Q2361: base_find — template selection is textual via ids hash

## Question
Does `Rest::Base.base_find` collapse two distinct identities into one when an unprivileged attacker submits the `ids:` hash passed to `base_find`, whose values are interpolated into the request path at `base_find(session:, ids:, params:)`, called by every generated `find`/`all` with caller-supplied `ids` and `params`? Show that `get_path` picks a template by matching available ids, so a crafted `ids` hash selects a different template than intended, that CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted is violated, and that the consequence is High - SSRF: an authenticated request carrying the app's credentials is driven to an unintended host.

## Target
- File/function: `lib/shopify_api/rest/base.rb` -> `Rest::Base.base_find`
- Entrypoint: `base_find(session:, ids:, params:)`, called by every generated `find`/`all` with caller-supplied `ids` and `params`
- Attacker controls: the `ids:` hash passed to `base_find`, whose values are interpolated into the request path
- Exploit idea: `get_path` picks a template by matching available ids, so a crafted `ids` hash selects a different template than intended
- Invariant to test: CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted
- Expected Immunefi impact: High - SSRF: an authenticated request carrying the app's credentials is driven to an unintended host (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest + WebMock: call a generated resource's `find` with an `ids` value containing `/` and assert the recorded request path
