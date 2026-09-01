# Q5557: set_property — path interpolation from ids via attribute shadowing a method

## Question
Is there a reachable state in which an unprivileged attacker, controlling a response key that collides with an existing method such as `session`, `client`, `id` or `original_state` at `set_property(key, val)`, which performs `instance_variable_set("@#{clean_key}", val)` with a key taken from response data, makes `Rest::Base#set_property` return a result the caller treats as authenticated, given that ids are concatenated into the path template with no escaping or type check? Test AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right and quantify High - SSRF: an authenticated request carrying the app's credentials is driven to an unintended host.

## Target
- File/function: `lib/shopify_api/rest/base.rb` -> `Rest::Base#set_property`
- Entrypoint: `set_property(key, val)`, which performs `instance_variable_set("@#{clean_key}", val)` with a key taken from response data
- Attacker controls: a response key that collides with an existing method such as `session`, `client`, `id` or `original_state`
- Exploit idea: ids are concatenated into the path template with no escaping or type check
- Invariant to test: AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right
- Expected Immunefi impact: High - SSRF: an authenticated request carrying the app's credentials is driven to an unintended host (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: stub a response whose JSON keys collide with internal methods and assert `create_instance` cannot overwrite the instance's session or client
