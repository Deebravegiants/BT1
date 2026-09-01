# Q950: parse_check_result — unanchored host match via response-controlled callbackUrl

## Question
Trace `Registrations::Http#parse_check_result` from `parse_check_result(body)`, which reads `callbackUrl`, `includeFields`, `metafieldNamespaces` and `filter` out of a GraphQL response with the `callbackUrl` returned by the check query, compared against the desired address to decide whether to re-register: because the `^#{Context.host_name}` test is a prefix match on an unescaped interpolation, so a look-alike host passes, does the value that was verified stop being the value that is used? Prove the break against AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right and map it to Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`).

## Target
- File/function: `lib/shopify_api/webhooks/registrations/http.rb` -> `Registrations::Http#parse_check_result`
- Entrypoint: `parse_check_result(body)`, which reads `callbackUrl`, `includeFields`, `metafieldNamespaces` and `filter` out of a GraphQL response
- Attacker controls: the `callbackUrl` returned by the check query, compared against the desired address to decide whether to re-register
- Exploit idea: the `^#{Context.host_name}` test is a prefix match on an unescaped interpolation, so a look-alike host passes
- Invariant to test: AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right
- Expected Immunefi impact: Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`) (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert a regex-metacharacter host name does not widen what `callback_address` accepts
