# Q2954: setup? — thread-local, not request-local via host / ENV['HOST']

## Question
Can an unprivileged attacker reach `Context.setup?` through `setup?`, which only checks that four strings are non-empty while supplying the `host` value, parsed by `host_name`/`host_scheme` and used to build redirect URIs and webhook callback addresses, so that `active_session` is thread-local; on a pooled server a session can outlive the request that set it, breaking the requirement that SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host, and ending in Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`)?

## Target
- File/function: `lib/shopify_api/context.rb` -> `Context.setup?`
- Entrypoint: `setup?`, which only checks that four strings are non-empty
- Attacker controls: the `host` value, parsed by `host_name`/`host_scheme` and used to build redirect URIs and webhook callback addresses
- Exploit idea: `active_session` is thread-local; on a pooled server a session can outlive the request that set it
- Invariant to test: SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host
- Expected Immunefi impact: Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`) (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert a crafted `api_version` cannot make `load_rest_resources` touch a path outside `lib/shopify_api/rest/resources`
