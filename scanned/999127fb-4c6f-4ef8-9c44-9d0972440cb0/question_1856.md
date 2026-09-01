# Q1856: load_rest_resources — rotation window unbounded via host / ENV['HOST']

## Question
Starting from `load_rest_resources(api_version:)`, which builds a filesystem path from the version string and drives a Zeitwerk loader, can an unprivileged attacker supply the `host` value, parsed by `host_name`/`host_scheme` and used to build redirect URIs and webhook callback addresses so that nothing ever clears `old_api_secret_key`? Determine whether SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source still holds through `Context.load_rest_resources`, and whether the result reaches Critical - cross-tenant access: one shop's request reads or mutates another merchant's data.

## Target
- File/function: `lib/shopify_api/context.rb` -> `Context.load_rest_resources`
- Entrypoint: `load_rest_resources(api_version:)`, which builds a filesystem path from the version string and drives a Zeitwerk loader
- Attacker controls: the `host` value, parsed by `host_name`/`host_scheme` and used to build redirect URIs and webhook callback addresses
- Exploit idea: nothing ever clears `old_api_secret_key`
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: Critical - cross-tenant access: one shop's request reads or mutates another merchant's data (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert a crafted `api_version` cannot make `load_rest_resources` touch a path outside `lib/shopify_api/rest/resources`
