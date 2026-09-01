# Q1067: save — path interpolation from ids via attribute name with punctuation

## Question
If an unprivileged attacker submits a response key containing `-`, `?`, `!`, spaces or `@`, after `clean_key` rewriting to `save(update_object:)`, which chooses verb and path via `deduce_write_verb` and `deduce_write_path`, does `Rest::Base#save` end up acting on a value that was never authenticated, because ids are concatenated into the path template with no escaping or type check? Close the question on SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source and on High - scope or expiry check bypass granting an operation the session was never authorized for.

## Target
- File/function: `lib/shopify_api/rest/base.rb` -> `Rest::Base#save`
- Entrypoint: `save(update_object:)`, which chooses verb and path via `deduce_write_verb` and `deduce_write_path`
- Attacker controls: a response key containing `-`, `?`, `!`, spaces or `@`, after `clean_key` rewriting
- Exploit idea: ids are concatenated into the path template with no escaping or type check
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: High - scope or expiry check bypass granting an operation the session was never authorized for (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `params:` values are query-escaped in the recorded request and cannot introduce a second query or a fragment
