# Q1990: build_check_query — regex injection via regex metacharacters in host

## Question
Does `Registrations::Http#build_check_query` collapse two distinct identities into one when an unprivileged attacker submits a `Context.host_name` containing regex metacharacters, since it is interpolated into a pattern unescaped at `build_check_query`, which interpolates `@topic` into a GraphQL document? Show that an unescaped interpolation into a `Regexp` changes what the match accepts, that SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source is violated, and that the consequence is Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`).

## Target
- File/function: `lib/shopify_api/webhooks/registrations/http.rb` -> `Registrations::Http#build_check_query`
- Entrypoint: `build_check_query`, which interpolates `@topic` into a GraphQL document
- Attacker controls: a `Context.host_name` containing regex metacharacters, since it is interpolated into a pattern unescaped
- Exploit idea: an unescaped interpolation into a `Regexp` changes what the match accepts
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`) (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `callback_address` never returns a host outside the app's own origin
