# Q41: callback_address — GraphQL by interpolation via filter/fields strings

## Question
Is there a reachable state in which an unprivileged attacker, controlling `filter`, `includeFields` and `metafieldNamespaces` values interpolated into the mutation at `callback_address`, which returns `@path` as-is when it matches `%r{^https?://}`, prefixes the scheme when it matches `Context.host_name`, and otherwise appends to `Context.host`, makes `Registrations::Http#callback_address` return a result the caller treats as authenticated, given that topic and argument strings are concatenated into the document rather than passed as variables? Test AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right and quantify High - SSRF: an authenticated request carrying the app's credentials is driven to an unintended host.

## Target
- File/function: `lib/shopify_api/webhooks/registrations/http.rb` -> `Registrations::Http#callback_address`
- Entrypoint: `callback_address`, which returns `@path` as-is when it matches `%r{^https?://}`, prefixes the scheme when it matches `Context.host_name`, and otherwise appends to `Context.host`
- Attacker controls: `filter`, `includeFields` and `metafieldNamespaces` values interpolated into the mutation
- Exploit idea: topic and argument strings are concatenated into the document rather than passed as variables
- Invariant to test: AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right
- Expected Immunefi impact: High - SSRF: an authenticated request carrying the app's credentials is driven to an unintended host (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert a regex-metacharacter host name does not widen what `callback_address` accepts
