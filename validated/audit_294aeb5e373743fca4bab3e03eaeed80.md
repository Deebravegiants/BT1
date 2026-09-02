### Title
Unauthenticated, attacker-controlled cookie value is trusted verbatim as an authenticated session-store key - (File: `lib/shopify_api/utils/session_utils.rb`)

### Summary
`SessionUtils.current_session_id` derives a session-store key either from a cryptographically verified JWT (`jwt_session_id`, format `"#{shop}_#{user_id}"`) or, when no ID token is supplied, from the raw, unvalidated `shopify_app_session` cookie via `cookie_session_id`. The cookie path performs no signature check, no correlation to server-issued state, and no shape restriction, so an attacker can submit a self-crafted cookie in exactly the `"#{shop}_#{user_id}"` shape produced by the authenticated path and have it accepted as if it had passed JWT verification.

### Finding Description
The broken binding, stated as an equality that should NOT hold but does:
`cookie_session_id(cookies) == jwt_session_id(shop, user_id)` for attacker-chosen `shop`/`user_id`, with no possession of a valid Shopify-signed JWT.

Code path: [1](#0-0)  shows `current_session_id` branching on `Context.embedded?` and the presence of `shopify_id_token`. When a token is present it goes through `session_id_from_shopify_id_token`, which validates the JWT via `Auth::JwtPayload.new(id_token)` and derives the key with `jwt_session_id(shop, T.must(payload.sub))` (format `"#{shop}_#{user_id}"`) as seen at [2](#0-1) . When no token is present (embedded fallback) or when the app is non-embedded, the code instead calls `cookie_session_id`, defined at [3](#0-2) , which does nothing but return `cookies[SESSION_COOKIE_NAME]` verbatim - no HMAC, no signature, no comparison against a server-generated value.

The `shopify_app_session` cookie itself is only ever set by the gem to a CSRF nonce during `begin_auth` (`cookie.value = state`) or to `session.id` / `""` after `validate_auth_callback`, per [4](#0-3)  and [5](#0-4) . None of that matters to an attacker, because the attacker is not relying on the legitimate cookie value at all - they are simply setting the `Cookie: shopify_app_session=<value>` header on their own outbound HTTP request to the host app. `cookie_session_id` accepts any string unconditionally and hands it back to the caller as a trusted session key.

Attacker request: any HTTP request to the app with header `Cookie: shopify_app_session=shop.myshopify.com_42` and no `Authorization: Bearer <jwt>` header (or in a non-embedded app, no id token is ever expected in the first place, so this path always runs). `current_session_id(nil, {"shopify_app_session" => "shop.myshopify.com_42"}, true)` returns `"shop.myshopify.com_42"` with zero validation.

None of the existing guards intervene: `HmacValidator.validate` and the `state` comparison only run inside `validate_auth_callback` during the OAuth handshake, not on every request; `JwtPayload`'s `aud`/`iss`/`exp` checks only execute inside the JWT branch, which is skipped entirely on the cookie path; `Context.embedded?`/`Context.setup?`/`Context.private?` only select which branch runs, they add no cryptographic verification to the cookie branch; Sorbet typing only enforces that the value is a `String`, not that it originated from a trusted source.

### Impact Explanation
If the host app uses the returned session ID to look up a stored `Session` (containing `access_token`) - which is the documented purpose of `current_session_id` - an attacker who supplies a guessed or enumerated `"#{shop}_#{user_id}"` (or `"offline_#{shop}"`) string in their own cookie header can retrieve another merchant's or staff member's session/access token from the app's session storage. Shop domains are public/enumerable and staff user IDs are frequently small sequential integers, making the guessable-key space small. This is repeatable against arbitrary victims by simply varying the cookie value per request, giving cross-tenant access to another tenant's session/access token - matching the Critical "cross-tenant access" category.

### Likelihood Explanation
Exploitability depends entirely on the host app choosing to rely on the cookie fallback (embedded app without an ID token present, or any non-embedded app, both of which always take this branch per [1](#0-0) ) and using the returned string directly as a session-storage lookup key without additional validation - which is exactly the pattern the gem's own API (`current_session_id`) is designed to support. The attacker needs no secrets, only the ability to set an arbitrary cookie on their own request and knowledge/guesses of a shop domain and small integer user ID. Cost per attempt is a single HTTP request; the attack is fully repeatable and scriptable.

### Recommendation
`cookie_session_id` must not return the raw, client-supplied cookie value as a trusted session key. The gem should either (a) sign/HMAC the session cookie value when it is set in `validate_auth_callback` and verify that signature in `cookie_session_id` before returning it, or (b) treat the cookie only as an opaque browser-session correlator that is itself looked up against a server-side mapping created at OAuth completion time, never accepting attacker-supplied values in the `"#{shop}_#{user_id}"`/`"offline_#{shop}"` shape without proof of origin.

### Proof of Concept
```ruby
# test/utils/session_utils_test.rb (conceptual addition)
def test_cookie_fallback_accepts_forged_session_id_shape
  ShopifyAPI::Context.setup(..., is_embedded: true)

  forged_cookie = { "shopify_app_session" => "victim-shop.myshopify.com_42" }

  # No JWT supplied, no signature of any kind checked
  result = ShopifyAPI::Utils::SessionUtils.current_session_id(nil, forged_cookie, true)

  # Equality claimed broken: forged value is accepted verbatim,
  # identical in shape to jwt_session_id("victim-shop.myshopify.com", "42")
  assert_equal(
    ShopifyAPI::Utils::SessionUtils.jwt_session_id("victim-shop.myshopify.com", "42"),
    result,
  )
end
```
This demonstrates that `SessionUtils.current_session_id` returns a key structurally identical to one produced by a verified JWT, without performing any JWT validation, HMAC check, or origin verification on the cookie value.

### Citations

**File:** lib/shopify_api/utils/session_utils.rb (L19-37)
```ruby
        def current_session_id(shopify_id_token, cookies, online)
          if Context.embedded?
            if shopify_id_token
              id_token = shopify_id_token.gsub("Bearer ", "")
              session_id_from_shopify_id_token(id_token: id_token, online: online)
            else
              # falling back to session cookie
              raise Errors::CookieNotFoundError, "JWT token or Session cookie not found for app" unless
                cookies && cookies[Auth::Oauth::SessionCookie::SESSION_COOKIE_NAME]

              cookie_session_id(cookies)
            end
          else
            raise Errors::CookieNotFoundError, "Session cookie not found for app" unless
              cookies && cookies[Auth::Oauth::SessionCookie::SESSION_COOKIE_NAME]

            cookie_session_id(cookies)
          end
        end
```

**File:** lib/shopify_api/utils/session_utils.rb (L45-61)
```ruby
        def session_id_from_shopify_id_token(id_token:, online:)
          raise Errors::MissingJwtTokenError, "Missing Shopify ID Token" if id_token.nil? || id_token.empty?

          payload = Auth::JwtPayload.new(id_token)
          shop = payload.shop

          if online
            jwt_session_id(shop, T.must(payload.sub))
          else
            offline_session_id(shop)
          end
        end

        sig { params(shop: String, user_id: String).returns(String) }
        def jwt_session_id(shop, user_id)
          "#{shop}_#{user_id}"
        end
```

**File:** lib/shopify_api/utils/session_utils.rb (L68-71)
```ruby
        sig { params(cookies: T::Hash[String, String]).returns(T.nilable(String)) }
        def cookie_session_id(cookies)
          cookies[Auth::Oauth::SessionCookie::SESSION_COOKIE_NAME]
        end
```

**File:** lib/shopify_api/auth/oauth.rb (L36-38)
```ruby
          state = SecureRandom.alphanumeric(NONCE_LENGTH)

          cookie = SessionCookie.new(value: state, expires: Time.now + 60)
```

**File:** lib/shopify_api/auth/oauth.rb (L100-110)
```ruby
          cookie = if Context.embedded?
            SessionCookie.new(
              value: "",
              expires: Time.now,
            )
          else
            SessionCookie.new(
              value: session.id,
              expires: session.expires ? session.expires : nil,
            )
          end
```
