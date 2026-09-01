# Q4703: save — method shadowing via nested has_many/has_one

## Question
Is there a reachable state in which an unprivileged attacker, controlling nested objects whose class is resolved from the attribute name at `save(update_object:)`, which chooses verb and path via `deduce_write_verb` and `deduce_write_path`, makes `Rest::Base#save` return a result the caller treats as authenticated, given that a property write can shadow or overwrite internal state such as the session or client held on the instance? Test SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source and quantify High - scope or expiry check bypass granting an operation the session was never authorized for.

## Target
- File/function: `lib/shopify_api/rest/base.rb` -> `Rest::Base#save`
- Entrypoint: `save(update_object:)`, which chooses verb and path via `deduce_write_verb` and `deduce_write_path`
- Attacker controls: nested objects whose class is resolved from the attribute name
- Exploit idea: a property write can shadow or overwrite internal state such as the session or client held on the instance
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: High - scope or expiry check bypass granting an operation the session was never authorized for (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `params:` values are query-escaped in the recorded request and cannot introduce a second query or a fragment
