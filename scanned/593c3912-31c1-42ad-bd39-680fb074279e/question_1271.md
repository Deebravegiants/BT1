# Q1271: parse_check_result — GraphQL by interpolation via host_name prefix match

## Question
Can a path whose prefix merely matches `Context.host_name` under an unanchored `%r{^#{Context.host_name}}` test, e.g. `example.com.evil.example/hook`, supplied by an unprivileged attacker at `parse_check_result(body)`, which reads `callbackUrl`, `includeFields`, `metafieldNamespaces` and `filter` out of a GraphQL response, make `Registrations::Http#parse_check_result` and the code consuming its result disagree, given that topic and argument strings are concatenated into the document rather than passed as variables? The binding to test is AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right; the impact to prove is High - credential or token leakage into log output or error messages.

## Target
- File/function: `lib/shopify_api/webhooks/registrations/http.rb` -> `Registrations::Http#parse_check_result`
- Entrypoint: `parse_check_result(body)`, which reads `callbackUrl`, `includeFields`, `metafieldNamespaces` and `filter` out of a GraphQL response
- Attacker controls: a path whose prefix merely matches `Context.host_name` under an unanchored `%r{^#{Context.host_name}}` test, e.g. `example.com.evil.example/hook`
- Exploit idea: topic and argument strings are concatenated into the document rather than passed as variables
- Invariant to test: AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right
- Expected Immunefi impact: High - credential or token leakage into log output or error messages (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert a regex-metacharacter host name does not widen what `callback_address` accepts
