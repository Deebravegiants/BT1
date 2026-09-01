# Q1795: initialize — canonicalisation gap via host param

## Question
If an unprivileged attacker submits the base64url `host` parameter, signed but never decoded or validated as a Shopify admin origin to `AuthQuery.new(code:, shop:, timestamp:, state:, host:, hmac:)`, built by the host app directly from the callback query string, does `AuthQuery#initialize` end up acting on a value that was never authenticated, because the string reconstructed by `URI.encode_www_form` is not byte-identical to what Shopify signed, so verification depends on incidental encoding? Close the question on BYTE IDENTITY: the bytes passed to `compute_signature` == the bytes later parsed and acted on and on Critical - cross-tenant access: one shop's request reads or mutates another merchant's data.

## Target
- File/function: `lib/shopify_api/auth/oauth/auth_query.rb` -> `AuthQuery#initialize`
- Entrypoint: `AuthQuery.new(code:, shop:, timestamp:, state:, host:, hmac:)`, built by the host app directly from the callback query string
- Attacker controls: the base64url `host` parameter, signed but never decoded or validated as a Shopify admin origin
- Exploit idea: the string reconstructed by `URI.encode_www_form` is not byte-identical to what Shopify signed, so verification depends on incidental encoding
- Invariant to test: BYTE IDENTITY: the bytes passed to `compute_signature` == the bytes later parsed and acted on
- Expected Immunefi impact: Critical - cross-tenant access: one shop's request reads or mutates another merchant's data (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: sign a canonical query with the test secret, mutate an out-of-coverage field, and assert `validate` still returns true
