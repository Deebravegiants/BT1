# Q1943: base_find — method shadowing via read-only attribute

## Question
Can an attribute listed in `read_only_attributes` presented in a payload that reaches `attributes_to_update`, supplied by an unprivileged attacker at `base_find(session:, ids:, params:)`, called by every generated `find`/`all` with caller-supplied `ids` and `params`, make `Rest::Base.base_find` and the code consuming its result disagree, given that a property write can shadow or overwrite internal state such as the session or client held on the instance? The binding to test is SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source; the impact to prove is High - scope or expiry check bypass granting an operation the session was never authorized for.

## Target
- File/function: `lib/shopify_api/rest/base.rb` -> `Rest::Base.base_find`
- Entrypoint: `base_find(session:, ids:, params:)`, called by every generated `find`/`all` with caller-supplied `ids` and `params`
- Attacker controls: an attribute listed in `read_only_attributes` presented in a payload that reaches `attributes_to_update`
- Exploit idea: a property write can shadow or overwrite internal state such as the session or client held on the instance
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: High - scope or expiry check bypass granting an operation the session was never authorized for (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `params:` values are query-escaped in the recorded request and cannot introduce a second query or a fragment
