# Q4488: from — equality omits the token via online/offline flip

## Question
Starting from `Session.from(shop:, access_token_response:)`, which mints `"#{shop}_#{associated_user.id}"` or `"offline_#{shop}"`, can an unprivileged attacker supply an `is_online` value inconsistent with `associated_user`, since `@is_online` defaults to `!associated_user.nil?` so that `Session#==` compares many fields; a caller using it to decide sameness may treat two sessions with different credentials as equal? Determine whether SESSION DERIVATION: a session id is derived only from bytes authenticated under `Context.api_secret_key` still holds through `Auth::Session.from`, and whether the result reaches High - scope or expiry check bypass granting an operation the session was never authorized for.

## Target
- File/function: `lib/shopify_api/auth/session.rb` -> `Auth::Session.from`
- Entrypoint: `Session.from(shop:, access_token_response:)`, which mints `"#{shop}_#{associated_user.id}"` or `"offline_#{shop}"`
- Attacker controls: an `is_online` value inconsistent with `associated_user`, since `@is_online` defaults to `!associated_user.nil?`
- Exploit idea: `Session#==` compares many fields; a caller using it to decide sameness may treat two sessions with different credentials as equal
- Invariant to test: SESSION DERIVATION: a session id is derived only from bytes authenticated under `Context.api_secret_key`
- Expected Immunefi impact: High - scope or expiry check bypass granting an operation the session was never authorized for (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest: construct sessions for shops containing `_` and assert `Session.from` ids are injective across (shop, user) pairs
