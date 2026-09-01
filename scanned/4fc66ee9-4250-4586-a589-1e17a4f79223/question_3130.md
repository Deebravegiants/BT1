# Q3130: load_rest_resources — version becomes a path via rest_disabled

## Question
Starting from `load_rest_resources(api_version:)`, which builds a filesystem path from the version string and drives a Zeitwerk loader, can an unprivileged attacker supply the `rest_disabled` flag, which decides whether the REST client raises so that `api_version.gsub("-","_")` is concatenated into a filesystem path before `Dir.exist?`? Determine whether SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host still holds through `Context.load_rest_resources`, and whether the result reaches Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`).

## Target
- File/function: `lib/shopify_api/context.rb` -> `Context.load_rest_resources`
- Entrypoint: `load_rest_resources(api_version:)`, which builds a filesystem path from the version string and drives a Zeitwerk loader
- Attacker controls: the `rest_disabled` flag, which decides whether the REST client raises
- Exploit idea: `api_version.gsub("-","_")` is concatenated into a filesystem path before `Dir.exist?`
- Invariant to test: SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host
- Expected Immunefi impact: Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`) (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `activate_session` is cleared at the end of a request cycle so a pooled thread cannot serve a stale tenant
