# Q3845: base_find — path interpolation from ids via response-driven attribute names

## Question
Does `Rest::Base.base_find` collapse two distinct identities into one when an unprivileged attacker submits attribute names arriving in API response JSON, which become `public_send("#{attribute}=")` and `instance_variable_set("@#{clean_key}")` targets at `base_find(session:, ids:, params:)`, called by every generated `find`/`all` with caller-supplied `ids` and `params`? Show that ids are concatenated into the path template with no escaping or type check, that SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source is violated, and that the consequence is High - SSRF: an authenticated request carrying the app's credentials is driven to an unintended host.

## Target
- File/function: `lib/shopify_api/rest/base.rb` -> `Rest::Base.base_find`
- Entrypoint: `base_find(session:, ids:, params:)`, called by every generated `find`/`all` with caller-supplied `ids` and `params`
- Attacker controls: attribute names arriving in API response JSON, which become `public_send("#{attribute}=")` and `instance_variable_set("@#{clean_key}")` targets
- Exploit idea: ids are concatenated into the path template with no escaping or type check
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: High - SSRF: an authenticated request carrying the app's credentials is driven to an unintended host (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `params:` values are query-escaped in the recorded request and cannot introduce a second query or a fragment
