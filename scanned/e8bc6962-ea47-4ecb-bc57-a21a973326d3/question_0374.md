# Q374: subscription_args — unanchored host match via regex metacharacters in host

## Question
If an unprivileged attacker submits a `Context.host_name` containing regex metacharacters, since it is interpolated into a pattern unescaped to `subscription_args`, which forwards `callbackUrl`, `includeFields`, `metafieldNamespaces` and `filter`, does `Registrations::Http#subscription_args` end up acting on a value that was never authenticated, because the `^#{Context.host_name}` test is a prefix match on an unescaped interpolation, so a look-alike host passes? Close the question on AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right and on Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`).

## Target
- File/function: `lib/shopify_api/webhooks/registrations/http.rb` -> `Registrations::Http#subscription_args`
- Entrypoint: `subscription_args`, which forwards `callbackUrl`, `includeFields`, `metafieldNamespaces` and `filter`
- Attacker controls: a `Context.host_name` containing regex metacharacters, since it is interpolated into a pattern unescaped
- Exploit idea: the `^#{Context.host_name}` test is a prefix match on an unescaped interpolation, so a look-alike host passes
- Invariant to test: AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right
- Expected Immunefi impact: Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`) (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert a regex-metacharacter host name does not widen what `callback_address` accepts
