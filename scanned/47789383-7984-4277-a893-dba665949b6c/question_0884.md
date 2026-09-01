# Q884: save — read-only filter applied late via session argument

## Question
Does `Rest::Base#save` collapse two distinct identities into one when an unprivileged attacker submits the `session:` argument threaded through `base_find` and `save`, which decides whose access token the resource call carries at `save(update_object:)`, which chooses verb and path via `deduce_write_verb` and `deduce_write_path`? Show that the read-only filter runs at serialisation time, after values have already been set on the instance, that SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source is violated, and that the consequence is Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`).

## Target
- File/function: `lib/shopify_api/rest/base.rb` -> `Rest::Base#save`
- Entrypoint: `save(update_object:)`, which chooses verb and path via `deduce_write_verb` and `deduce_write_path`
- Attacker controls: the `session:` argument threaded through `base_find` and `save`, which decides whose access token the resource call carries
- Exploit idea: the read-only filter runs at serialisation time, after values have already been set on the instance
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`) (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `params:` values are query-escaped in the recorded request and cannot introduce a second query or a fragment
