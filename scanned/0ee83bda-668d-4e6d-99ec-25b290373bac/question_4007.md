# Q4007: expired? — equality omits the token via caller-supplied id

## Question
If an unprivileged attacker submits the `id:` keyword, which lets a session be constructed under any storage key to `expired?`, which returns false whenever `@expires` is nil, does `Auth::Session#expired?` end up acting on a value that was never authenticated, because `Session#==` compares many fields; a caller using it to decide sameness may treat two sessions with different credentials as equal? Close the question on SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source and on Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`).

## Target
- File/function: `lib/shopify_api/auth/session.rb` -> `Auth::Session#expired?`
- Entrypoint: `expired?`, which returns false whenever `@expires` is nil
- Attacker controls: the `id:` keyword, which lets a session be constructed under any storage key
- Exploit idea: `Session#==` compares many fields; a caller using it to decide sameness may treat two sessions with different credentials as equal
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`) (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `copy_attributes_from` refuses to change `shop` on a session whose `id` encodes a different shop
