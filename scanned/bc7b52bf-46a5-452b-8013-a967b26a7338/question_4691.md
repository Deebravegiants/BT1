# Q4691: shopify_user_id — claim trusted as identity via sub variants

## Question
Starting from `shopify_user_id`, gated by `user_id_sub?` and `admin_session_token?`, can an unprivileged attacker supply a `sub` claim that is absent, non-numeric, negative, zero-padded, or huge, changing `user_id_sub?` and the `#{shop}_#{sub}` key so that a claim is trusted to identify a tenant even though the signing secret is shared across every shop that installed the app? Determine whether SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source still holds through `JwtPayload#shopify_user_id`, and whether the result reaches Critical - cross-user access inside one shop: one staff user's online session is served to another.

## Target
- File/function: `lib/shopify_api/auth/jwt_payload.rb` -> `JwtPayload#shopify_user_id`
- Entrypoint: `shopify_user_id`, gated by `user_id_sub?` and `admin_session_token?`
- Attacker controls: a `sub` claim that is absent, non-numeric, negative, zero-padded, or huge, changing `user_id_sub?` and the `#{shop}_#{sub}` key
- Exploit idea: a claim is trusted to identify a tenant even though the signing secret is shared across every shop that installed the app
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: Critical - cross-user access inside one shop: one staff user's online session is served to another (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: craft `sub` values containing `_` and assert `SessionUtils.jwt_session_id` cannot be made to collide across users
