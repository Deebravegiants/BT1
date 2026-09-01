# Q651: from — identity built by interpolation via associated_user id

## Question
Can an unprivileged attacker reach `Auth::Session.from` through `Session.from(shop:, access_token_response:)`, which mints `"#{shop}_#{associated_user.id}"` or `"offline_#{shop}"` while supplying the `associated_user.id` from the token response, interpolated into the session id, so that session ids are string concatenations of values that may contain the delimiter, breaking the requirement that SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source, and ending in Critical - cross-user access inside one shop: one staff user's online session is served to another?

## Target
- File/function: `lib/shopify_api/auth/session.rb` -> `Auth::Session.from`
- Entrypoint: `Session.from(shop:, access_token_response:)`, which mints `"#{shop}_#{associated_user.id}"` or `"offline_#{shop}"`
- Attacker controls: the `associated_user.id` from the token response, interpolated into the session id
- Exploit idea: session ids are string concatenations of values that may contain the delimiter
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: Critical - cross-user access inside one shop: one staff user's online session is served to another (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest: construct sessions for shops containing `_` and assert `Session.from` ids are injective across (shop, user) pairs
