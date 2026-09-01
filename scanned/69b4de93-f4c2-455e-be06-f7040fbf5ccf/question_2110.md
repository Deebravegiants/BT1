# Q2110: parse_check_result — scheme-carrying path trusted via host_name prefix match

## Question
If an unprivileged attacker submits a path whose prefix merely matches `Context.host_name` under an unanchored `%r{^#{Context.host_name}}` test, e.g. `example.com.evil.example/hook` to `parse_check_result(body)`, which reads `callbackUrl`, `includeFields`, `metafieldNamespaces` and `filter` out of a GraphQL response, does `Registrations::Http#parse_check_result` end up acting on a value that was never authenticated, because a path that already looks like a URL is used verbatim as the delivery destination for the merchant's webhook data? Close the question on SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source and on Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`).

## Target
- File/function: `lib/shopify_api/webhooks/registrations/http.rb` -> `Registrations::Http#parse_check_result`
- Entrypoint: `parse_check_result(body)`, which reads `callbackUrl`, `includeFields`, `metafieldNamespaces` and `filter` out of a GraphQL response
- Attacker controls: a path whose prefix merely matches `Context.host_name` under an unanchored `%r{^#{Context.host_name}}` test, e.g. `example.com.evil.example/hook`
- Exploit idea: a path that already looks like a URL is used verbatim as the delivery destination for the merchant's webhook data
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`) (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `callback_address` never returns a host outside the app's own origin
