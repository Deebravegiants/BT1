# Q4240: offline_session_id — key is predictable via Bearer interior match

## Question
Trace `SessionUtils.offline_session_id` from `offline_session_id(shop)`, a bare `"offline_#{shop}"` interpolation with an `Authorization` value where `gsub("Bearer ", "")` strips an interior occurrence and changes the token that gets decoded: because `offline_#{shop}` and `#{shop}_#{user_id}` are fully derivable from public information, does the value that was verified stop being the value that is used? Prove the break against SESSION DERIVATION: a session id is derived only from bytes authenticated under `Context.api_secret_key` and map it to Critical - cross-tenant access: one shop's request reads or mutates another merchant's data.

## Target
- File/function: `lib/shopify_api/utils/session_utils.rb` -> `SessionUtils.offline_session_id`
- Entrypoint: `offline_session_id(shop)`, a bare `"offline_#{shop}"` interpolation
- Attacker controls: an `Authorization` value where `gsub("Bearer ", "")` strips an interior occurrence and changes the token that gets decoded
- Exploit idea: `offline_#{shop}` and `#{shop}_#{user_id}` are fully derivable from public information
- Invariant to test: SESSION DERIVATION: a session id is derived only from bytes authenticated under `Context.api_secret_key`
- Expected Immunefi impact: Critical - cross-tenant access: one shop's request reads or mutates another merchant's data (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert an embedded app rejects a request with no `Authorization` header rather than falling back to the cookie
