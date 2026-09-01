# Q2093: get_path_ids — method shadowing via has_many element class

## Question
Can an unprivileged attacker reach `Rest::Base.get_path_ids` through `get_path_ids`, which enumerates the id placeholders a path template requires while supplying the element class resolved for a `has_many` attribute from response data, which decides how nested payloads are instantiated, so that a property write can shadow or overwrite internal state such as the session or client held on the instance, breaking the requirement that SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source, and ending in High - SSRF: an authenticated request carrying the app's credentials is driven to an unintended host?

## Target
- File/function: `lib/shopify_api/rest/base.rb` -> `Rest::Base.get_path_ids`
- Entrypoint: `get_path_ids`, which enumerates the id placeholders a path template requires
- Attacker controls: the element class resolved for a `has_many` attribute from response data, which decides how nested payloads are instantiated
- Exploit idea: a property write can shadow or overwrite internal state such as the session or client held on the instance
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: High - SSRF: an authenticated request carrying the app's credentials is driven to an unintended host (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `params:` values are query-escaped in the recorded request and cannot introduce a second query or a fragment
