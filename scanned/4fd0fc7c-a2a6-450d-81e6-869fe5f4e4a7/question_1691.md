# Q1691: get_path_ids — path interpolation from ids via params hash

## Question
Can the `params:` hash, forwarded as the outgoing query string, supplied by an unprivileged attacker at `get_path_ids`, which enumerates the id placeholders a path template requires, make `Rest::Base.get_path_ids` and the code consuming its result disagree, given that ids are concatenated into the path template with no escaping or type check? The binding to test is SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source; the impact to prove is High - scope or expiry check bypass granting an operation the session was never authorized for.

## Target
- File/function: `lib/shopify_api/rest/base.rb` -> `Rest::Base.get_path_ids`
- Entrypoint: `get_path_ids`, which enumerates the id placeholders a path template requires
- Attacker controls: the `params:` hash, forwarded as the outgoing query string
- Exploit idea: ids are concatenated into the path template with no escaping or type check
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: High - scope or expiry check bypass granting an operation the session was never authorized for (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `params:` values are query-escaped in the recorded request and cannot introduce a second query or a fragment
