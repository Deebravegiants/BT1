# Q5243: save — cursor trusted via original_state diff

## Question
Can an unprivileged attacker reach `Rest::Base#save` through `save(update_object:)`, which chooses verb and path via `deduce_write_verb` and `deduce_write_path` while supplying the `original_state` snapshot that `attributes_to_update` diffs against, deciding which fields a `PUT` actually sends, so that page-info cursors from a response are replayed into the next authenticated request without validation, breaking the requirement that SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source, and ending in High - scope or expiry check bypass granting an operation the session was never authorized for?

## Target
- File/function: `lib/shopify_api/rest/base.rb` -> `Rest::Base#save`
- Entrypoint: `save(update_object:)`, which chooses verb and path via `deduce_write_verb` and `deduce_write_path`
- Attacker controls: the `original_state` snapshot that `attributes_to_update` diffs against, deciding which fields a `PUT` actually sends
- Exploit idea: page-info cursors from a response are replayed into the next authenticated request without validation
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: High - scope or expiry check bypass granting an operation the session was never authorized for (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `params:` values are query-escaped in the recorded request and cannot introduce a second query or a fragment
