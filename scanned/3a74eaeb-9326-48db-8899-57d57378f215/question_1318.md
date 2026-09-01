# Q1318: shopify_user_id — no iss/dest binding via dest without scheme

## Question
Does `JwtPayload#shopify_user_id` collapse two distinct identities into one when an unprivileged attacker submits a `dest` claim that is not `https://<shop>` (no scheme, a path, a port, or multiple `https://` occurrences the unanchored `gsub` all strip) at `shopify_user_id`, gated by `user_id_sub?` and `admin_session_token?`? Show that the constructor validates `aud` only; nothing asserts `iss` and `dest` describe the same shop, that CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted is violated, and that the consequence is Critical - exfiltration of the app's `client_secret` and/or the OAuth authorization `code`.

## Target
- File/function: `lib/shopify_api/auth/jwt_payload.rb` -> `JwtPayload#shopify_user_id`
- Entrypoint: `shopify_user_id`, gated by `user_id_sub?` and `admin_session_token?`
- Attacker controls: a `dest` claim that is not `https://<shop>` (no scheme, a path, a port, or multiple `https://` occurrences the unanchored `gsub` all strip)
- Exploit idea: the constructor validates `aud` only; nothing asserts `iss` and `dest` describe the same shop
- Invariant to test: CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted
- Expected Immunefi impact: Critical - exfiltration of the app's `client_secret` and/or the OAuth authorization `code` (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `JwtPayload.new` raises for a `dest` outside `TRUSTED_SHOPIFY_DOMAINS`; if it does not, assert the resulting `HttpClient` base URI under WebMock
