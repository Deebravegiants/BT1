# Q3325: get_path — cursor trusted via has_many element class

## Question
Can an unprivileged attacker reach `Rest::Base.get_path` through `Rest::Base.get_path(http_method:, operation:, entity:, ids:)`, which matches a path template and interpolates ids while supplying the element class resolved for a `has_many` attribute from response data, which decides how nested payloads are instantiated, so that page-info cursors from a response are replayed into the next authenticated request without validation, breaking the requirement that AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right, and ending in High - SSRF: an authenticated request carrying the app's credentials is driven to an unintended host?

## Target
- File/function: `lib/shopify_api/rest/base.rb` -> `Rest::Base.get_path`
- Entrypoint: `Rest::Base.get_path(http_method:, operation:, entity:, ids:)`, which matches a path template and interpolates ids
- Attacker controls: the element class resolved for a `has_many` attribute from response data, which decides how nested payloads are instantiated
- Exploit idea: page-info cursors from a response are replayed into the next authenticated request without validation
- Invariant to test: AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right
- Expected Immunefi impact: High - SSRF: an authenticated request carrying the app's credentials is driven to an unintended host (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: stub a response whose JSON keys collide with internal methods and assert `create_instance` cannot overwrite the instance's session or client
