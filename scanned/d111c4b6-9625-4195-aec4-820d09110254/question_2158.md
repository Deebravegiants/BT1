# Q2158: setup — rotation window unbounded via old_api_secret_key

## Question
Does `Context.setup` collapse two distinct identities into one when an unprivileged attacker submits `old_api_secret_key`, which permanently widens the set of signatures and tokens accepted at `ShopifyAPI::Context.setup(...)`, which stores every security-relevant global including `api_secret_key`, `old_api_secret_key`, `host`, `api_host` and `scope`? Show that nothing ever clears `old_api_secret_key`, that SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host is violated, and that the consequence is Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`).

## Target
- File/function: `lib/shopify_api/context.rb` -> `Context.setup`
- Entrypoint: `ShopifyAPI::Context.setup(...)`, which stores every security-relevant global including `api_secret_key`, `old_api_secret_key`, `host`, `api_host` and `scope`
- Attacker controls: `old_api_secret_key`, which permanently widens the set of signatures and tokens accepted
- Exploit idea: nothing ever clears `old_api_secret_key`
- Invariant to test: SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host
- Expected Immunefi impact: Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`) (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `activate_session` is cleared at the end of a request cycle so a pooled thread cannot serve a stale tenant
