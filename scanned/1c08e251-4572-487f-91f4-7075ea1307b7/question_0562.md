# Q562: parse_check_result — scheme-carrying path trusted via regex metacharacters in host

## Question
Does `Registrations::Http#parse_check_result` collapse two distinct identities into one when an unprivileged attacker submits a `Context.host_name` containing regex metacharacters, since it is interpolated into a pattern unescaped at `parse_check_result(body)`, which reads `callbackUrl`, `includeFields`, `metafieldNamespaces` and `filter` out of a GraphQL response? Show that a path that already looks like a URL is used verbatim as the delivery destination for the merchant's webhook data, that SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source is violated, and that the consequence is Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`).

## Target
- File/function: `lib/shopify_api/webhooks/registrations/http.rb` -> `Registrations::Http#parse_check_result`
- Entrypoint: `parse_check_result(body)`, which reads `callbackUrl`, `includeFields`, `metafieldNamespaces` and `filter` out of a GraphQL response
- Attacker controls: a `Context.host_name` containing regex metacharacters, since it is interpolated into a pattern unescaped
- Exploit idea: a path that already looks like a URL is used verbatim as the delivery destination for the merchant's webhook data
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`) (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `callback_address` never returns a host outside the app's own origin
