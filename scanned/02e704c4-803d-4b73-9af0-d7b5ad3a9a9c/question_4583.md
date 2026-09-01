# Q4583: auth_base_uri — redirect target unbound via expired cookie

## Question
Trace `Oauth.auth_base_uri` from the private `auth_base_uri(shop)` that builds `"https://#{shop}/admin"` with no call to `ShopValidator` with a `SessionCookie` presented after its 60-second `expires` has passed, which the gem never re-checks on the callback side: because `redirect_uri` is built from `Context.host` + `redirect_path` at authorize time but never re-verified at callback time, does the value that was verified stop being the value that is used? Prove the break against SESSION DERIVATION: a session id is derived only from bytes authenticated under `Context.api_secret_key` and map it to Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`).

## Target
- File/function: `lib/shopify_api/auth/oauth.rb` -> `Oauth.auth_base_uri`
- Entrypoint: the private `auth_base_uri(shop)` that builds `"https://#{shop}/admin"` with no call to `ShopValidator`
- Attacker controls: a `SessionCookie` presented after its 60-second `expires` has passed, which the gem never re-checks on the callback side
- Exploit idea: `redirect_uri` is built from `Context.host` + `redirect_path` at authorize time but never re-verified at callback time
- Invariant to test: SESSION DERIVATION: a session id is derived only from bytes authenticated under `Context.api_secret_key`
- Expected Immunefi impact: Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`) (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert the returned `SessionCookie#value` is never equal to `session.id` for an embedded app, and that the cookie is cleared
