# Q825: expired? — temp restores unconditionally via scope string

## Question
Is there a reachable state in which an unprivileged attacker, controlling the `scope` string from the token response, parsed by `AuthScopes` with no validation at `expired?`, which returns false whenever `@expires` is nil, makes `Auth::Session#expired?` return a result the caller treats as authenticated, given that the `ensure` block restores whatever was captured, which under nesting or threading may not be the caller's session? Test SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host and quantify Critical - cross-tenant access: one shop's request reads or mutates another merchant's data.

## Target
- File/function: `lib/shopify_api/auth/session.rb` -> `Auth::Session#expired?`
- Entrypoint: `expired?`, which returns false whenever `@expires` is nil
- Attacker controls: the `scope` string from the token response, parsed by `AuthScopes` with no validation
- Exploit idea: the `ensure` block restores whatever was captured, which under nesting or threading may not be the caller's session
- Invariant to test: SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host
- Expected Immunefi impact: Critical - cross-tenant access: one shop's request reads or mutates another merchant's data (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest: construct sessions for shops containing `_` and assert `Session.from` ids are injective across (shop, user) pairs
