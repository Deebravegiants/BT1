# Q887: callback_address — GraphQL by interpolation via regex metacharacters in host

## Question
Trace `Registrations::Http#callback_address` from `callback_address`, which returns `@path` as-is when it matches `%r{^https?://}`, prefixes the scheme when it matches `Context.host_name`, and otherwise appends to `Context.host` with a `Context.host_name` containing regex metacharacters, since it is interpolated into a pattern unescaped: because topic and argument strings are concatenated into the document rather than passed as variables, does the value that was verified stop being the value that is used? Prove the break against AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right and map it to High - credential or token leakage into log output or error messages.

## Target
- File/function: `lib/shopify_api/webhooks/registrations/http.rb` -> `Registrations::Http#callback_address`
- Entrypoint: `callback_address`, which returns `@path` as-is when it matches `%r{^https?://}`, prefixes the scheme when it matches `Context.host_name`, and otherwise appends to `Context.host`
- Attacker controls: a `Context.host_name` containing regex metacharacters, since it is interpolated into a pattern unescaped
- Exploit idea: topic and argument strings are concatenated into the document rather than passed as variables
- Invariant to test: AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right
- Expected Immunefi impact: High - credential or token leakage into log output or error messages (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert a regex-metacharacter host name does not widen what `callback_address` accepts
