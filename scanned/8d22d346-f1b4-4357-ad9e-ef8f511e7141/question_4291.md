# Q4291: copy_attributes_from — identity built by interpolation via nil expires

## Question
Can an unprivileged attacker reach `Auth::Session#copy_attributes_from` through `copy_attributes_from(other)`, which overwrites every attribute except `id` while supplying an access-token response with no `expires_in`, leaving `@expires` nil and `expired?` permanently false, so that session ids are string concatenations of values that may contain the delimiter, breaking the requirement that SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source, and ending in Critical - cross-user access inside one shop: one staff user's online session is served to another?

## Target
- File/function: `lib/shopify_api/auth/session.rb` -> `Auth::Session#copy_attributes_from`
- Entrypoint: `copy_attributes_from(other)`, which overwrites every attribute except `id`
- Attacker controls: an access-token response with no `expires_in`, leaving `@expires` nil and `expired?` permanently false
- Exploit idea: session ids are string concatenations of values that may contain the delimiter
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: Critical - cross-user access inside one shop: one staff user's online session is served to another (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `expired?` is true, not false, for a session with no expiry once its token is past any plausible lifetime
