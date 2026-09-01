# Q824: build_check_query — unanchored host match via host_name prefix match

## Question
Trace `Registrations::Http#build_check_query` from `build_check_query`, which interpolates `@topic` into a GraphQL document with a path whose prefix merely matches `Context.host_name` under an unanchored `%r{^#{Context.host_name}}` test, e.g. `example.com.evil.example/hook`: because the `^#{Context.host_name}` test is a prefix match on an unescaped interpolation, so a look-alike host passes, does the value that was verified stop being the value that is used? Prove the break against AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right and map it to Critical - cross-tenant access: one shop's request reads or mutates another merchant's data.

## Target
- File/function: `lib/shopify_api/webhooks/registrations/http.rb` -> `Registrations::Http#build_check_query`
- Entrypoint: `build_check_query`, which interpolates `@topic` into a GraphQL document
- Attacker controls: a path whose prefix merely matches `Context.host_name` under an unanchored `%r{^#{Context.host_name}}` test, e.g. `example.com.evil.example/hook`
- Exploit idea: the `^#{Context.host_name}` test is a prefix match on an unescaped interpolation, so a look-alike host passes
- Invariant to test: AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right
- Expected Immunefi impact: Critical - cross-tenant access: one shop's request reads or mutates another merchant's data (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert a regex-metacharacter host name does not widen what `callback_address` accepts
