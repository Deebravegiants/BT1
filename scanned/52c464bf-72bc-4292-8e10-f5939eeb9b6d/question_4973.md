# Q4973: set_property — query forwarded verbatim via response-driven attribute names

## Question
If an unprivileged attacker submits attribute names arriving in API response JSON, which become `public_send("#{attribute}=")` and `instance_variable_set("@#{clean_key}")` targets to `set_property(key, val)`, which performs `instance_variable_set("@#{clean_key}", val)` with a key taken from response data, does `Rest::Base#set_property` end up acting on a value that was never authenticated, because `params:` is passed through to the outgoing query with the merchant's token attached? Close the question on SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source and on High - SSRF: an authenticated request carrying the app's credentials is driven to an unintended host.

## Target
- File/function: `lib/shopify_api/rest/base.rb` -> `Rest::Base#set_property`
- Entrypoint: `set_property(key, val)`, which performs `instance_variable_set("@#{clean_key}", val)` with a key taken from response data
- Attacker controls: attribute names arriving in API response JSON, which become `public_send("#{attribute}=")` and `instance_variable_set("@#{clean_key}")` targets
- Exploit idea: `params:` is passed through to the outgoing query with the merchant's token attached
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: High - SSRF: an authenticated request carrying the app's credentials is driven to an unintended host (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `params:` values are query-escaped in the recorded request and cannot introduce a second query or a fragment
