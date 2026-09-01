# Q1239: activate_session — version becomes a path via scope default

## Question
Can an unprivileged attacker reach `Context.activate_session` through `Context.activate_session(session)` and `Context.active_session`, backed by a `Concurrent::ThreadLocalVar` while supplying the default `scope`, used by `begin_auth` whenever no override is passed, so that `api_version.gsub("-","_")` is concatenated into a filesystem path before `Dir.exist?`, breaking the requirement that AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right, and ending in Critical - authentication bypass: a forged or unsigned request is accepted as authentic by the app?

## Target
- File/function: `lib/shopify_api/context.rb` -> `Context.activate_session`
- Entrypoint: `Context.activate_session(session)` and `Context.active_session`, backed by a `Concurrent::ThreadLocalVar`
- Attacker controls: the default `scope`, used by `begin_auth` whenever no override is passed
- Exploit idea: `api_version.gsub("-","_")` is concatenated into a filesystem path before `Dir.exist?`
- Invariant to test: AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right
- Expected Immunefi impact: Critical - authentication bypass: a forged or unsigned request is accepted as authentic by the app (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest: run two threads through `Session.temp` and assert neither observes the other's active session
