# Q866: build_check_query — re-register decision from response via regex metacharacters in host

## Question
Trace `Registrations::Http#build_check_query` from `build_check_query`, which interpolates `@topic` into a GraphQL document with a `Context.host_name` containing regex metacharacters, since it is interpolated into a pattern unescaped: because whether the callback address is overwritten is decided by comparing against attacker-influenceable response content, does the value that was verified stop being the value that is used? Prove the break against AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right and map it to Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`).

## Target
- File/function: `lib/shopify_api/webhooks/registrations/http.rb` -> `Registrations::Http#build_check_query`
- Entrypoint: `build_check_query`, which interpolates `@topic` into a GraphQL document
- Attacker controls: a `Context.host_name` containing regex metacharacters, since it is interpolated into a pattern unescaped
- Exploit idea: whether the callback address is overwritten is decided by comparing against attacker-influenceable response content
- Invariant to test: AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right
- Expected Immunefi impact: Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`) (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert a regex-metacharacter host name does not widen what `callback_address` accepts
