# Q2230: parse_check_result — regex injection via regex metacharacters in host

## Question
Can a `Context.host_name` containing regex metacharacters, since it is interpolated into a pattern unescaped, supplied by an unprivileged attacker at `parse_check_result(body)`, which reads `callbackUrl`, `includeFields`, `metafieldNamespaces` and `filter` out of a GraphQL response, make `Registrations::Http#parse_check_result` and the code consuming its result disagree, given that an unescaped interpolation into a `Regexp` changes what the match accepts? The binding to test is SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source; the impact to prove is Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`).

## Target
- File/function: `lib/shopify_api/webhooks/registrations/http.rb` -> `Registrations::Http#parse_check_result`
- Entrypoint: `parse_check_result(body)`, which reads `callbackUrl`, `includeFields`, `metafieldNamespaces` and `filter` out of a GraphQL response
- Attacker controls: a `Context.host_name` containing regex metacharacters, since it is interpolated into a pattern unescaped
- Exploit idea: an unescaped interpolation into a `Regexp` changes what the match accepts
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`) (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `callback_address` never returns a host outside the app's own origin
