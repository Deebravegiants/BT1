# Q788: load_rest_resources — host header decoupled from connection via host / ENV['HOST']

## Question
Can the `host` value, parsed by `host_name`/`host_scheme` and used to build redirect URIs and webhook callback addresses, supplied by an unprivileged attacker at `load_rest_resources(api_version:)`, which builds a filesystem path from the version string and drives a Zeitwerk loader, make `Context.load_rest_resources` and the code consuming its result disagree, given that with `api_host` set, `Host` is `session.shop` while the socket goes elsewhere? The binding to test is SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source; the impact to prove is Critical - cross-tenant access: one shop's request reads or mutates another merchant's data.

## Target
- File/function: `lib/shopify_api/context.rb` -> `Context.load_rest_resources`
- Entrypoint: `load_rest_resources(api_version:)`, which builds a filesystem path from the version string and drives a Zeitwerk loader
- Attacker controls: the `host` value, parsed by `host_name`/`host_scheme` and used to build redirect URIs and webhook callback addresses
- Exploit idea: with `api_host` set, `Host` is `session.shop` while the socket goes elsewhere
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: Critical - cross-tenant access: one shop's request reads or mutates another merchant's data (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert a crafted `api_version` cannot make `load_rest_resources` touch a path outside `lib/shopify_api/rest/resources`
