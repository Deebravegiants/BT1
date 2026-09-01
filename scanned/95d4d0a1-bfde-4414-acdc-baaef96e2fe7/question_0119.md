# Q119: build_check_query — GraphQL by interpolation via response-controlled callbackUrl

## Question
Can an unprivileged attacker reach `Registrations::Http#build_check_query` through `build_check_query`, which interpolates `@topic` into a GraphQL document while supplying the `callbackUrl` returned by the check query, compared against the desired address to decide whether to re-register, so that topic and argument strings are concatenated into the document rather than passed as variables, breaking the requirement that AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right, and ending in High - credential or token leakage into log output or error messages?

## Target
- File/function: `lib/shopify_api/webhooks/registrations/http.rb` -> `Registrations::Http#build_check_query`
- Entrypoint: `build_check_query`, which interpolates `@topic` into a GraphQL document
- Attacker controls: the `callbackUrl` returned by the check query, compared against the desired address to decide whether to re-register
- Exploit idea: topic and argument strings are concatenated into the document rather than passed as variables
- Invariant to test: AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right
- Expected Immunefi impact: High - credential or token leakage into log output or error messages (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert a regex-metacharacter host name does not widen what `callback_address` accepts
