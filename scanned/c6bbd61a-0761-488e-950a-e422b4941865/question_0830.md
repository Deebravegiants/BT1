# Q830: load_rest_resources — rotation window unbounded via scope default

## Question
Can the default `scope`, used by `begin_auth` whenever no override is passed, supplied by an unprivileged attacker at `load_rest_resources(api_version:)`, which builds a filesystem path from the version string and drives a Zeitwerk loader, make `Context.load_rest_resources` and the code consuming its result disagree, given that nothing ever clears `old_api_secret_key`? The binding to test is SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host; the impact to prove is Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`).

## Target
- File/function: `lib/shopify_api/context.rb` -> `Context.load_rest_resources`
- Entrypoint: `load_rest_resources(api_version:)`, which builds a filesystem path from the version string and drives a Zeitwerk loader
- Attacker controls: the default `scope`, used by `begin_auth` whenever no override is passed
- Exploit idea: nothing ever clears `old_api_secret_key`
- Invariant to test: SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host
- Expected Immunefi impact: Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`) (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert a crafted `api_version` cannot make `load_rest_resources` touch a path outside `lib/shopify_api/rest/resources`
