# Q1645: parse_check_result — unanchored host match via path with scheme

## Question
Can an unprivileged attacker reach `Registrations::Http#parse_check_result` through `parse_check_result(body)`, which reads `callbackUrl`, `includeFields`, `metafieldNamespaces` and `filter` out of a GraphQL response while supplying a registration `path` already carrying `http://` or `https://`, returned verbatim as the callback address, so that the `^#{Context.host_name}` test is a prefix match on an unescaped interpolation, so a look-alike host passes, breaking the requirement that SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source, and ending in High - SSRF: an authenticated request carrying the app's credentials is driven to an unintended host?

## Target
- File/function: `lib/shopify_api/webhooks/registrations/http.rb` -> `Registrations::Http#parse_check_result`
- Entrypoint: `parse_check_result(body)`, which reads `callbackUrl`, `includeFields`, `metafieldNamespaces` and `filter` out of a GraphQL response
- Attacker controls: a registration `path` already carrying `http://` or `https://`, returned verbatim as the callback address
- Exploit idea: the `^#{Context.host_name}` test is a prefix match on an unescaped interpolation, so a look-alike host passes
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: High - SSRF: an authenticated request carrying the app's credentials is driven to an unintended host (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `callback_address` never returns a host outside the app's own origin
