# Q2123: to_hash — path interpolation from ids via params hash

## Question
Does `Rest::Base#to_hash` collapse two distinct identities into one when an unprivileged attacker submits the `params:` hash, forwarded as the outgoing query string at `to_hash(saving)`, which walks `instance_variables` and filters `read_only_attributes`? Show that ids are concatenated into the path template with no escaping or type check, that SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source is violated, and that the consequence is High - scope or expiry check bypass granting an operation the session was never authorized for.

## Target
- File/function: `lib/shopify_api/rest/base.rb` -> `Rest::Base#to_hash`
- Entrypoint: `to_hash(saving)`, which walks `instance_variables` and filters `read_only_attributes`
- Attacker controls: the `params:` hash, forwarded as the outgoing query string
- Exploit idea: ids are concatenated into the path template with no escaping or type check
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: High - scope or expiry check bypass granting an operation the session was never authorized for (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `params:` values are query-escaped in the recorded request and cannot introduce a second query or a fragment
