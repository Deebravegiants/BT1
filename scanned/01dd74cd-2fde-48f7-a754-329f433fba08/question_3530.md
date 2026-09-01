# Q3530: decode_token — shop never domain-validated via sub variants

## Question
Does `JwtPayload#decode_token` collapse two distinct identities into one when an unprivileged attacker submits a `sub` claim that is absent, non-numeric, negative, zero-padded, or huge, changing `user_id_sub?` and the `#{shop}_#{sub}` key at the private `decode_token`, a `JWT.decode(token, secret, true, leeway: 10, algorithm: 'HS256')`? Show that the derived `shop` string is used as a request host and a session key without `ShopValidator`, that CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted is violated, and that the consequence is Critical - cross-tenant access: one shop's request reads or mutates another merchant's data.

## Target
- File/function: `lib/shopify_api/auth/jwt_payload.rb` -> `JwtPayload#decode_token`
- Entrypoint: the private `decode_token`, a `JWT.decode(token, secret, true, leeway: 10, algorithm: 'HS256')`
- Attacker controls: a `sub` claim that is absent, non-numeric, negative, zero-padded, or huge, changing `user_id_sub?` and the `#{shop}_#{sub}` key
- Exploit idea: the derived `shop` string is used as a request host and a session key without `ShopValidator`
- Invariant to test: CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted
- Expected Immunefi impact: Critical - cross-tenant access: one shop's request reads or mutates another merchant's data (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: craft `sub` values containing `_` and assert `SessionUtils.jwt_session_id` cannot be made to collide across users
