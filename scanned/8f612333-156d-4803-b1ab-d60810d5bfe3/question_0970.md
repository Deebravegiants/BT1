# Q970: build_check_query — scheme-carrying path trusted via topic string

## Question
Can the `@topic` value interpolated into `build_check_query` unquoted, supplied by an unprivileged attacker at `build_check_query`, which interpolates `@topic` into a GraphQL document, make `Registrations::Http#build_check_query` and the code consuming its result disagree, given that a path that already looks like a URL is used verbatim as the delivery destination for the merchant's webhook data? The binding to test is SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source; the impact to prove is Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`).

## Target
- File/function: `lib/shopify_api/webhooks/registrations/http.rb` -> `Registrations::Http#build_check_query`
- Entrypoint: `build_check_query`, which interpolates `@topic` into a GraphQL document
- Attacker controls: the `@topic` value interpolated into `build_check_query` unquoted
- Exploit idea: a path that already looks like a URL is used verbatim as the delivery destination for the merchant's webhook data
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`) (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `callback_address` never returns a host outside the app's own origin
