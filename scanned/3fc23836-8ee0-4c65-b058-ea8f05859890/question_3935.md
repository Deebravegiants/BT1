# Q3935: set_property — query forwarded verbatim via params hash

## Question
Starting from `set_property(key, val)`, which performs `instance_variable_set("@#{clean_key}", val)` with a key taken from response data, can an unprivileged attacker supply the `params:` hash, forwarded as the outgoing query string so that `params:` is passed through to the outgoing query with the merchant's token attached? Determine whether SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source still holds through `Rest::Base#set_property`, and whether the result reaches High - scope or expiry check bypass granting an operation the session was never authorized for.

## Target
- File/function: `lib/shopify_api/rest/base.rb` -> `Rest::Base#set_property`
- Entrypoint: `set_property(key, val)`, which performs `instance_variable_set("@#{clean_key}", val)` with a key taken from response data
- Attacker controls: the `params:` hash, forwarded as the outgoing query string
- Exploit idea: `params:` is passed through to the outgoing query with the merchant's token attached
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: High - scope or expiry check bypass granting an operation the session was never authorized for (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `params:` values are query-escaped in the recorded request and cannot introduce a second query or a fragment
