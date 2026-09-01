# Q2020: build_check_query — scheme-carrying path trusted via response-controlled callbackUrl

## Question
Can the `callbackUrl` returned by the check query, compared against the desired address to decide whether to re-register, supplied by an unprivileged attacker at `build_check_query`, which interpolates `@topic` into a GraphQL document, make `Registrations::Http#build_check_query` and the code consuming its result disagree, given that a path that already looks like a URL is used verbatim as the delivery destination for the merchant's webhook data? The binding to test is SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source; the impact to prove is Critical - cross-tenant access: one shop's request reads or mutates another merchant's data.

## Target
- File/function: `lib/shopify_api/webhooks/registrations/http.rb` -> `Registrations::Http#build_check_query`
- Entrypoint: `build_check_query`, which interpolates `@topic` into a GraphQL document
- Attacker controls: the `callbackUrl` returned by the check query, compared against the desired address to decide whether to re-register
- Exploit idea: a path that already looks like a URL is used verbatim as the delivery destination for the merchant's webhook data
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: Critical - cross-tenant access: one shop's request reads or mutates another merchant's data (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `callback_address` never returns a host outside the app's own origin
