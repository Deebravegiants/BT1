# Q1597: parse_check_result — re-register decision from response via filter/fields strings

## Question
Starting from `parse_check_result(body)`, which reads `callbackUrl`, `includeFields`, `metafieldNamespaces` and `filter` out of a GraphQL response, can an unprivileged attacker supply `filter`, `includeFields` and `metafieldNamespaces` values interpolated into the mutation so that whether the callback address is overwritten is decided by comparing against attacker-influenceable response content? Determine whether SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source still holds through `Registrations::Http#parse_check_result`, and whether the result reaches High - SSRF: an authenticated request carrying the app's credentials is driven to an unintended host.

## Target
- File/function: `lib/shopify_api/webhooks/registrations/http.rb` -> `Registrations::Http#parse_check_result`
- Entrypoint: `parse_check_result(body)`, which reads `callbackUrl`, `includeFields`, `metafieldNamespaces` and `filter` out of a GraphQL response
- Attacker controls: `filter`, `includeFields` and `metafieldNamespaces` values interpolated into the mutation
- Exploit idea: whether the callback address is overwritten is decided by comparing against attacker-influenceable response content
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: High - SSRF: an authenticated request carrying the app's credentials is driven to an unintended host (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `callback_address` never returns a host outside the app's own origin
