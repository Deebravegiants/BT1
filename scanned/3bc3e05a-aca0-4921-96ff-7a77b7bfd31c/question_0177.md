# Q177: == — one cookie, two meanings via cookie value

## Question
Does `Oauth::SessionCookie#==` collapse two distinct identities into one when an unprivileged attacker submits the cookie value, which in the non-embedded callback branch is `session.id` itself at `SessionCookie#==`, which compares name, value and expiry? Show that the same cookie name carries the pre-auth nonce and the post-auth session id, so a value from one phase is accepted in the other, that SESSION DERIVATION: a session id is derived only from bytes authenticated under `Context.api_secret_key` is violated, and that the consequence is Critical - cross-tenant access: one shop's request reads or mutates another merchant's data.

## Target
- File/function: `lib/shopify_api/auth/oauth/session_cookie.rb` -> `Oauth::SessionCookie#==`
- Entrypoint: `SessionCookie#==`, which compares name, value and expiry
- Attacker controls: the cookie value, which in the non-embedded callback branch is `session.id` itself
- Exploit idea: the same cookie name carries the pre-auth nonce and the post-auth session id, so a value from one phase is accepted in the other
- Invariant to test: SESSION DERIVATION: a session id is derived only from bytes authenticated under `Context.api_secret_key`
- Expected Immunefi impact: Critical - cross-tenant access: one shop's request reads or mutates another merchant's data (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert the cookie issued by `begin_auth` cannot be replayed after its `expires` has passed
