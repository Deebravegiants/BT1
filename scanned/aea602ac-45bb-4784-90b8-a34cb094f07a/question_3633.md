# Q3633: save — path interpolation from ids via original_state diff

## Question
Can an unprivileged attacker reach `Rest::Base#save` through `save(update_object:)`, which chooses verb and path via `deduce_write_verb` and `deduce_write_path` while supplying the `original_state` snapshot that `attributes_to_update` diffs against, deciding which fields a `PUT` actually sends, so that ids are concatenated into the path template with no escaping or type check, breaking the requirement that CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted, and ending in High - SSRF: an authenticated request carrying the app's credentials is driven to an unintended host?

## Target
- File/function: `lib/shopify_api/rest/base.rb` -> `Rest::Base#save`
- Entrypoint: `save(update_object:)`, which chooses verb and path via `deduce_write_verb` and `deduce_write_path`
- Attacker controls: the `original_state` snapshot that `attributes_to_update` diffs against, deciding which fields a `PUT` actually sends
- Exploit idea: ids are concatenated into the path template with no escaping or type check
- Invariant to test: CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted
- Expected Immunefi impact: High - SSRF: an authenticated request carrying the app's credentials is driven to an unintended host (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest + WebMock: call a generated resource's `find` with an `ids` value containing `/` and assert the recorded request path
