# Q1235: subscription_args — scheme-carrying path trusted via path with scheme

## Question
If an unprivileged attacker submits a registration `path` already carrying `http://` or `https://`, returned verbatim as the callback address to `subscription_args`, which forwards `callbackUrl`, `includeFields`, `metafieldNamespaces` and `filter`, does `Registrations::Http#subscription_args` end up acting on a value that was never authenticated, because a path that already looks like a URL is used verbatim as the delivery destination for the merchant's webhook data? Close the question on AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right and on High - credential or token leakage into log output or error messages.

## Target
- File/function: `lib/shopify_api/webhooks/registrations/http.rb` -> `Registrations::Http#subscription_args`
- Entrypoint: `subscription_args`, which forwards `callbackUrl`, `includeFields`, `metafieldNamespaces` and `filter`
- Attacker controls: a registration `path` already carrying `http://` or `https://`, returned verbatim as the callback address
- Exploit idea: a path that already looks like a URL is used verbatim as the delivery destination for the merchant's webhook data
- Invariant to test: AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right
- Expected Immunefi impact: High - credential or token leakage into log output or error messages (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert a regex-metacharacter host name does not widen what `callback_address` accepts
