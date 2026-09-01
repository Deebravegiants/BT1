# Q2200: build_check_query — GraphQL by interpolation via path with scheme

## Question
Does `Registrations::Http#build_check_query` collapse two distinct identities into one when an unprivileged attacker submits a registration `path` already carrying `http://` or `https://`, returned verbatim as the callback address at `build_check_query`, which interpolates `@topic` into a GraphQL document? Show that topic and argument strings are concatenated into the document rather than passed as variables, that SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source is violated, and that the consequence is Critical - cross-tenant access: one shop's request reads or mutates another merchant's data.

## Target
- File/function: `lib/shopify_api/webhooks/registrations/http.rb` -> `Registrations::Http#build_check_query`
- Entrypoint: `build_check_query`, which interpolates `@topic` into a GraphQL document
- Attacker controls: a registration `path` already carrying `http://` or `https://`, returned verbatim as the callback address
- Exploit idea: topic and argument strings are concatenated into the document rather than passed as variables
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: Critical - cross-tenant access: one shop's request reads or mutates another merchant's data (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `callback_address` never returns a host outside the app's own origin
