# Q4599: get_path — template selection is textual via original_state diff

## Question
Can an unprivileged attacker reach `Rest::Base.get_path` through `Rest::Base.get_path(http_method:, operation:, entity:, ids:)`, which matches a path template and interpolates ids while supplying the `original_state` snapshot that `attributes_to_update` diffs against, deciding which fields a `PUT` actually sends, so that `get_path` picks a template by matching available ids, so a crafted `ids` hash selects a different template than intended, breaking the requirement that CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted, and ending in High - scope or expiry check bypass granting an operation the session was never authorized for?

## Target
- File/function: `lib/shopify_api/rest/base.rb` -> `Rest::Base.get_path`
- Entrypoint: `Rest::Base.get_path(http_method:, operation:, entity:, ids:)`, which matches a path template and interpolates ids
- Attacker controls: the `original_state` snapshot that `attributes_to_update` diffs against, deciding which fields a `PUT` actually sends
- Exploit idea: `get_path` picks a template by matching available ids, so a crafted `ids` hash selects a different template than intended
- Invariant to test: CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted
- Expected Immunefi impact: High - scope or expiry check bypass granting an operation the session was never authorized for (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest + WebMock: call a generated resource's `find` with an `ids` value containing `/` and assert the recorded request path
