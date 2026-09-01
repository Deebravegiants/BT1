# Q5333: create_instance — method shadowing via response-driven attribute names

## Question
Is there a reachable state in which an unprivileged attacker, controlling attribute names arriving in API response JSON, which become `public_send("#{attribute}=")` and `instance_variable_set("@#{clean_key}")` targets at `create_instance(data:, session:, instance:)`, which builds objects from API response JSON via `public_send("#{attribute}=", ...)`, makes `Rest::Base.create_instance` return a result the caller treats as authenticated, given that a property write can shadow or overwrite internal state such as the session or client held on the instance? Test SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source and quantify High - SSRF: an authenticated request carrying the app's credentials is driven to an unintended host.

## Target
- File/function: `lib/shopify_api/rest/base.rb` -> `Rest::Base.create_instance`
- Entrypoint: `create_instance(data:, session:, instance:)`, which builds objects from API response JSON via `public_send("#{attribute}=", ...)`
- Attacker controls: attribute names arriving in API response JSON, which become `public_send("#{attribute}=")` and `instance_variable_set("@#{clean_key}")` targets
- Exploit idea: a property write can shadow or overwrite internal state such as the session or client held on the instance
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: High - SSRF: an authenticated request carrying the app's credentials is driven to an unintended host (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `params:` values are query-escaped in the recorded request and cannot introduce a second query or a fragment
