# Q5116: shop — claim trusted as identity via aud edge

## Question
Is there a reachable state in which an unprivileged attacker, controlling an `aud` claim that equals `Context.api_key` by type coercion rather than value (array form, numeric key) at `JwtPayload#shop`, computed as `@dest.gsub("https://", "")`, makes `JwtPayload#shop` return a result the caller treats as authenticated, given that a claim is trusted to identify a tenant even though the signing secret is shared across every shop that installed the app? Test SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host and quantify Critical - cross-user access inside one shop: one staff user's online session is served to another.

## Target
- File/function: `lib/shopify_api/auth/jwt_payload.rb` -> `JwtPayload#shop`
- Entrypoint: `JwtPayload#shop`, computed as `@dest.gsub("https://", "")`
- Attacker controls: an `aud` claim that equals `Context.api_key` by type coercion rather than value (array form, numeric key)
- Exploit idea: a claim is trusted to identify a tenant even though the signing secret is shared across every shop that installed the app
- Invariant to test: SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host
- Expected Immunefi impact: Critical - cross-user access inside one shop: one staff user's online session is served to another (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `JwtPayload.new` raises for a `dest` outside `TRUSTED_SHOPIFY_DOMAINS`; if it does not, assert the resulting `HttpClient` base URI under WebMock
