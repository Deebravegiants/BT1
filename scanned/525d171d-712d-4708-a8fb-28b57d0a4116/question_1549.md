# Q1549: subscription_args — unanchored host match via path with scheme

## Question
Does `Registrations::Http#subscription_args` collapse two distinct identities into one when an unprivileged attacker submits a registration `path` already carrying `http://` or `https://`, returned verbatim as the callback address at `subscription_args`, which forwards `callbackUrl`, `includeFields`, `metafieldNamespaces` and `filter`? Show that the `^#{Context.host_name}` test is a prefix match on an unescaped interpolation, so a look-alike host passes, that SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source is violated, and that the consequence is High - SSRF: an authenticated request carrying the app's credentials is driven to an unintended host.

## Target
- File/function: `lib/shopify_api/webhooks/registrations/http.rb` -> `Registrations::Http#subscription_args`
- Entrypoint: `subscription_args`, which forwards `callbackUrl`, `includeFields`, `metafieldNamespaces` and `filter`
- Attacker controls: a registration `path` already carrying `http://` or `https://`, returned verbatim as the callback address
- Exploit idea: the `^#{Context.host_name}` test is a prefix match on an unescaped interpolation, so a look-alike host passes
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: High - SSRF: an authenticated request carrying the app's credentials is driven to an unintended host (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `callback_address` never returns a host outside the app's own origin
