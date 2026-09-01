# Q1010: subscription_args — regex injection via host_name prefix match

## Question
Does `Registrations::Http#subscription_args` collapse two distinct identities into one when an unprivileged attacker submits a path whose prefix merely matches `Context.host_name` under an unanchored `%r{^#{Context.host_name}}` test, e.g. `example.com.evil.example/hook` at `subscription_args`, which forwards `callbackUrl`, `includeFields`, `metafieldNamespaces` and `filter`? Show that an unescaped interpolation into a `Regexp` changes what the match accepts, that AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right is violated, and that the consequence is Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`).

## Target
- File/function: `lib/shopify_api/webhooks/registrations/http.rb` -> `Registrations::Http#subscription_args`
- Entrypoint: `subscription_args`, which forwards `callbackUrl`, `includeFields`, `metafieldNamespaces` and `filter`
- Attacker controls: a path whose prefix merely matches `Context.host_name` under an unanchored `%r{^#{Context.host_name}}` test, e.g. `example.com.evil.example/hook`
- Exploit idea: an unescaped interpolation into a `Regexp` changes what the match accepts
- Invariant to test: AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right
- Expected Immunefi impact: Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`) (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert a regex-metacharacter host name does not widen what `callback_address` accepts
