# Q5473: create_instance — cursor trusted via attribute name with punctuation

## Question
Is there a reachable state in which an unprivileged attacker, controlling a response key containing `-`, `?`, `!`, spaces or `@`, after `clean_key` rewriting at `create_instance(data:, session:, instance:)`, which builds objects from API response JSON via `public_send("#{attribute}=", ...)`, makes `Rest::Base.create_instance` return a result the caller treats as authenticated, given that page-info cursors from a response are replayed into the next authenticated request without validation? Test AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right and quantify High - SSRF: an authenticated request carrying the app's credentials is driven to an unintended host.

## Target
- File/function: `lib/shopify_api/rest/base.rb` -> `Rest::Base.create_instance`
- Entrypoint: `create_instance(data:, session:, instance:)`, which builds objects from API response JSON via `public_send("#{attribute}=", ...)`
- Attacker controls: a response key containing `-`, `?`, `!`, spaces or `@`, after `clean_key` rewriting
- Exploit idea: page-info cursors from a response are replayed into the next authenticated request without validation
- Invariant to test: AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right
- Expected Immunefi impact: High - SSRF: an authenticated request carrying the app's credentials is driven to an unintended host (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: stub a response whose JSON keys collide with internal methods and assert `create_instance` cannot overwrite the instance's session or client
