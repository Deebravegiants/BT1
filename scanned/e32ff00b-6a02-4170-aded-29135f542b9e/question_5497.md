# Q5497: create_instance — path interpolation from ids via attribute name with punctuation

## Question
Does `Rest::Base.create_instance` collapse two distinct identities into one when an unprivileged attacker submits a response key containing `-`, `?`, `!`, spaces or `@`, after `clean_key` rewriting at `create_instance(data:, session:, instance:)`, which builds objects from API response JSON via `public_send("#{attribute}=", ...)`? Show that ids are concatenated into the path template with no escaping or type check, that AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right is violated, and that the consequence is High - SSRF: an authenticated request carrying the app's credentials is driven to an unintended host.

## Target
- File/function: `lib/shopify_api/rest/base.rb` -> `Rest::Base.create_instance`
- Entrypoint: `create_instance(data:, session:, instance:)`, which builds objects from API response JSON via `public_send("#{attribute}=", ...)`
- Attacker controls: a response key containing `-`, `?`, `!`, spaces or `@`, after `clean_key` rewriting
- Exploit idea: ids are concatenated into the path template with no escaping or type check
- Invariant to test: AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right
- Expected Immunefi impact: High - SSRF: an authenticated request carrying the app's credentials is driven to an unintended host (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: stub a response whose JSON keys collide with internal methods and assert `create_instance` cannot overwrite the instance's session or client
