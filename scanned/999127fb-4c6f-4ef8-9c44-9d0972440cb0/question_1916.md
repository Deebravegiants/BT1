# Q1916: copy_attributes_from — identity built by interpolation via associated_user id

## Question
Trace `Auth::Session#copy_attributes_from` from `copy_attributes_from(other)`, which overwrites every attribute except `id` with the `associated_user.id` from the token response, interpolated into the session id: because session ids are string concatenations of values that may contain the delimiter, does the value that was verified stop being the value that is used? Prove the break against SESSION DERIVATION: a session id is derived only from bytes authenticated under `Context.api_secret_key` and map it to Critical - cross-user access inside one shop: one staff user's online session is served to another.

## Target
- File/function: `lib/shopify_api/auth/session.rb` -> `Auth::Session#copy_attributes_from`
- Entrypoint: `copy_attributes_from(other)`, which overwrites every attribute except `id`
- Attacker controls: the `associated_user.id` from the token response, interpolated into the session id
- Exploit idea: session ids are string concatenations of values that may contain the delimiter
- Invariant to test: SESSION DERIVATION: a session id is derived only from bytes authenticated under `Context.api_secret_key`
- Expected Immunefi impact: Critical - cross-user access inside one shop: one staff user's online session is served to another (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `copy_attributes_from` refuses to change `shop` on a session whose `id` encodes a different shop
