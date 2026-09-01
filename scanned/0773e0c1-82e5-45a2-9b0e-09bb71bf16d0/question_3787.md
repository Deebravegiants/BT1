# Q3787: expired? — nil means valid via copy across identities

## Question
Can an unprivileged attacker reach `Auth::Session#expired?` through `expired?`, which returns false whenever `@expires` is nil while supplying a `copy_attributes_from` call that moves another shop's `shop` and `access_token` onto a session keeping its own `id`, so that `expired?` and `refresh_token_expired?` treat missing expiry as never-expiring, breaking the requirement that SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source, and ending in Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`)?

## Target
- File/function: `lib/shopify_api/auth/session.rb` -> `Auth::Session#expired?`
- Entrypoint: `expired?`, which returns false whenever `@expires` is nil
- Attacker controls: a `copy_attributes_from` call that moves another shop's `shop` and `access_token` onto a session keeping its own `id`
- Exploit idea: `expired?` and `refresh_token_expired?` treat missing expiry as never-expiring
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`) (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `expired?` is true, not false, for a session with no expiry once its token is past any plausible lifetime
