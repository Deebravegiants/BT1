# Q5485: create_instance — read-only filter applied late via has_many element class

## Question
Can the element class resolved for a `has_many` attribute from response data, which decides how nested payloads are instantiated, supplied by an unprivileged attacker at `create_instance(data:, session:, instance:)`, which builds objects from API response JSON via `public_send("#{attribute}=", ...)`, make `Rest::Base.create_instance` and the code consuming its result disagree, given that the read-only filter runs at serialisation time, after values have already been set on the instance? The binding to test is AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right; the impact to prove is High - SSRF: an authenticated request carrying the app's credentials is driven to an unintended host.

## Target
- File/function: `lib/shopify_api/rest/base.rb` -> `Rest::Base.create_instance`
- Entrypoint: `create_instance(data:, session:, instance:)`, which builds objects from API response JSON via `public_send("#{attribute}=", ...)`
- Attacker controls: the element class resolved for a `has_many` attribute from response data, which decides how nested payloads are instantiated
- Exploit idea: the read-only filter runs at serialisation time, after values have already been set on the instance
- Invariant to test: AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right
- Expected Immunefi impact: High - SSRF: an authenticated request carrying the app's credentials is driven to an unintended host (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: stub a response whose JSON keys collide with internal methods and assert `create_instance` cannot overwrite the instance's session or client
