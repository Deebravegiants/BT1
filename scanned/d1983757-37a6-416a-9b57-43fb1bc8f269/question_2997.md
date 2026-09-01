# Q2997: copy_attributes_from — copy preserves the key via copy across identities

## Question
Starting from `copy_attributes_from(other)`, which overwrites every attribute except `id`, can an unprivileged attacker supply a `copy_attributes_from` call that moves another shop's `shop` and `access_token` onto a session keeping its own `id` so that `copy_attributes_from` overwrites the shop and token while keeping the id, so a key silently starts pointing at a different tenant? Determine whether SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host still holds through `Auth::Session#copy_attributes_from`, and whether the result reaches Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`).

## Target
- File/function: `lib/shopify_api/auth/session.rb` -> `Auth::Session#copy_attributes_from`
- Entrypoint: `copy_attributes_from(other)`, which overwrites every attribute except `id`
- Attacker controls: a `copy_attributes_from` call that moves another shop's `shop` and `access_token` onto a session keeping its own `id`
- Exploit idea: `copy_attributes_from` overwrites the shop and token while keeping the id, so a key silently starts pointing at a different tenant
- Invariant to test: SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host
- Expected Immunefi impact: Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`) (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest: construct sessions for shops containing `_` and assert `Session.from` ids are injective across (shop, user) pairs
