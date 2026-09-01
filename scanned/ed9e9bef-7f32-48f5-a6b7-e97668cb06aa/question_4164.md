# Q4164: temp — equality omits the token via shop with separator

## Question
Is there a reachable state in which an unprivileged attacker, controlling a `shop` containing `_` so `"#{shop}_#{user_id}"` collides with another shop/user pair at `Session.temp(shop:, access_token:)`, which swaps `Context.active_session` around a block, makes `Auth::Session.temp` return a result the caller treats as authenticated, given that `Session#==` compares many fields; a caller using it to decide sameness may treat two sessions with different credentials as equal? Test SESSION DERIVATION: a session id is derived only from bytes authenticated under `Context.api_secret_key` and quantify Critical - theft of a merchant's refresh token, granting durable access after rotation.

## Target
- File/function: `lib/shopify_api/auth/session.rb` -> `Auth::Session.temp`
- Entrypoint: `Session.temp(shop:, access_token:)`, which swaps `Context.active_session` around a block
- Attacker controls: a `shop` containing `_` so `"#{shop}_#{user_id}"` collides with another shop/user pair
- Exploit idea: `Session#==` compares many fields; a caller using it to decide sameness may treat two sessions with different credentials as equal
- Invariant to test: SESSION DERIVATION: a session id is derived only from bytes authenticated under `Context.api_secret_key`
- Expected Immunefi impact: Critical - theft of a merchant's refresh token, granting durable access after rotation (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest: construct sessions for shops containing `_` and assert `Session.from` ids are injective across (shop, user) pairs
