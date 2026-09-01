# Q3086: setup? — setup? is a presence check via expiring_offline_access_tokens

## Question
Is there a reachable state in which an unprivileged attacker, controlling the `expiring_offline_access_tokens` flag, which changes token lifetime and the `expiring` body field at `setup?`, which only checks that four strings are non-empty, makes `Context.setup?` return a result the caller treats as authenticated, given that `setup?` proves four strings are non-empty, not that any of them is well-formed? Test SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host and quantify Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`).

## Target
- File/function: `lib/shopify_api/context.rb` -> `Context.setup?`
- Entrypoint: `setup?`, which only checks that four strings are non-empty
- Attacker controls: the `expiring_offline_access_tokens` flag, which changes token lifetime and the `expiring` body field
- Exploit idea: `setup?` proves four strings are non-empty, not that any of them is well-formed
- Invariant to test: SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host
- Expected Immunefi impact: Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`) (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert a crafted `api_version` cannot make `load_rest_resources` touch a path outside `lib/shopify_api/rest/resources`
