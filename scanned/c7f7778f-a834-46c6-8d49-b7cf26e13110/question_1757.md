# Q1757: subscription_args — re-register decision from response via response-controlled callbackUrl

## Question
Can an unprivileged attacker reach `Registrations::Http#subscription_args` through `subscription_args`, which forwards `callbackUrl`, `includeFields`, `metafieldNamespaces` and `filter` while supplying the `callbackUrl` returned by the check query, compared against the desired address to decide whether to re-register, so that whether the callback address is overwritten is decided by comparing against attacker-influenceable response content, breaking the requirement that AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right, and ending in High - SSRF: an authenticated request carrying the app's credentials is driven to an unintended host?

## Target
- File/function: `lib/shopify_api/webhooks/registrations/http.rb` -> `Registrations::Http#subscription_args`
- Entrypoint: `subscription_args`, which forwards `callbackUrl`, `includeFields`, `metafieldNamespaces` and `filter`
- Attacker controls: the `callbackUrl` returned by the check query, compared against the desired address to decide whether to re-register
- Exploit idea: whether the callback address is overwritten is decided by comparing against attacker-influenceable response content
- Invariant to test: AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right
- Expected Immunefi impact: High - SSRF: an authenticated request carrying the app's credentials is driven to an unintended host (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert a regex-metacharacter host name does not widen what `callback_address` accepts
