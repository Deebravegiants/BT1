# Q3817: refresh_token_expired? — nil means valid via associated_user id

## Question
Does `Auth::Session#refresh_token_expired?` collapse two distinct identities into one when an unprivileged attacker submits the `associated_user.id` from the token response, interpolated into the session id at `refresh_token_expired?`, which returns false whenever `@refresh_token_expires` is nil? Show that `expired?` and `refresh_token_expired?` treat missing expiry as never-expiring, that SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host is violated, and that the consequence is Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`).

## Target
- File/function: `lib/shopify_api/auth/session.rb` -> `Auth::Session#refresh_token_expired?`
- Entrypoint: `refresh_token_expired?`, which returns false whenever `@refresh_token_expires` is nil
- Attacker controls: the `associated_user.id` from the token response, interpolated into the session id
- Exploit idea: `expired?` and `refresh_token_expired?` treat missing expiry as never-expiring
- Invariant to test: SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host
- Expected Immunefi impact: Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`) (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `expired?` is true, not false, for a session with no expiry once its token is past any plausible lifetime
