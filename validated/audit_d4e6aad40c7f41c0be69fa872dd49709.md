### Title
Non-embedded session cookie value is a fully predictable, unsigned bearer identifier (`"offline_#{shop}"` / `"#{shop}_#{user_id}"`) with no MAC - ([File: lib/shopify_api/auth/oauth.rb], [File: lib/shopify_api/auth/oauth/session_cookie.rb], [File: lib/shopify_api/utils/session_utils.rb])

### Summary
`ShopifyAPI::Auth::Oauth.validate_auth_callback` sets the post-auth session cookie's `value` to `session.id`, and for offline sessions `session.id` is computed as `"offline_#{shop}"` by `SessionUtils.offline_session_id`, with no HMAC, signature, or any server-only secret mixed in. Because the `shop` domain is public information, any unprivileged attacker can synthesize this exact cookie value for an arbitrary target shop without ever needing to observe the victim's browser or steal a cookie.

### Finding Description
The broken binding, stated as an equality that should NOT hold but does:

`SessionCookie.new(value: session.id, expires: session.expires).value == SessionUtils.offline_session_id(shop)`

is true byte-for-byte, and `shop` is the only input — there is no per-browser nonce, no HMAC over `(shop, secret)`, and no random component.

Code path:
- `SessionCookie` is a plain `T::Struct` with only `name`, `value`, `expires` fields — no MAC/signature field exists anywhere on the struct: [1](#0-0) 
- In the non-embedded branch of `validate_auth_callback`, the cookie's `value` is set directly to `session.id`: [2](#0-1) 
- `session.id` for offline sessions is `"offline_#{shop}"`, a pure string interpolation of the (public) shop domain, with no secret material: [3](#0-2) 
- On subsequent requests, the host app is instructed (per this gem's own docs) to call `SessionUtils.current_session_id(nil, cookies, online)` to recover the session identifier straight from the cookie, with no HMAC/shop-consistency/state check performed anywhere in that method: [4](#0-3) 

Existing guards do not protect this path: `Utils::HmacValidator.validate` and the `state == auth_query.state` check are only used once, during the OAuth callback itself, to authenticate the *installation* request; they are never re-checked when a cookie is later presented to `current_session_id`. `JwtPayload`'s `aud`/`exp` checks only apply to the embedded, id-token branch, not to the cookie branch used by non-embedded apps. `ShopValidator.sanitize!` and `Context.embedded?`/`private?` have no bearing on the value stored in the cookie.

Attacker request: the attacker needs no secret — only the target's `.myshopify.com` domain (public, and trivially derivable from any storefront). They set a cookie named `shopify_app_session` with value `offline_<target-shop>.myshopify.com` on requests to the victim's app, hitting any endpoint that calls `ShopifyAPI::Utils::SessionUtils.current_session_id(nil, cookies, false)` as documented in `docs/getting_started.md`. The call returns the exact same session id string the legitimate merchant's browser holds, which the host app then uses to look up the persisted offline `Session` (containing the real Shopify access token) and serve/authenticate the request as that merchant — with no random or secret component this gem ever asked the host app to check.

### Impact Explanation
If the host app's session storage (built per this gem's documented contract) keys stored sessions by this identifier, an attacker who only knows a target shop's domain can present a cookie value they computed themselves — never having seen the merchant's real cookie — and be treated as that merchant's authenticated session, gaining access to the offline access token bound to the target's shop. This is a cross-tenant authentication bypass: the same technique works against any shop simply by substituting its domain into the string, so the blast radius spans every merchant using an app built on this gem's non-embedded/cookie flow. This matches "Critical - authentication bypass ... session token accepted" / "High - session fixation," since the session identifier requires no cryptographic secret to construct.

### Likelihood Explanation
Preconditions: the app must use the non-embedded, cookie-based flow documented in `docs/getting_started.md` and `docs/usage/oauth.md` (`ShopifyAPI::Auth::Oauth.validate_auth_callback` + `SessionUtils.current_session_id`), which is a first-class, explicitly documented usage of this gem — not a third-party misuse. Attacker cost is trivial (string concatenation of a public domain); no credentials, no MITM, no XSS, and no interaction with the victim are required. It is fully repeatable against any shop whose domain is known.

### Recommendation
Do not use a deterministic, secret-free string as the sole bearer value of the session cookie. Bind the cookie value to a value only the server can produce/verify, e.g. sign `session.id` with `Context.api_secret_key` (HMAC) and store/compare the MAC, or use a cryptographically random session token as the cookie value and map it server-side to `session.id`, rather than exposing the deterministic ID as the credential itself.

### Proof of Concept
```ruby
# test/auth/oauth_cookie_predictability_test.rb
require_relative "../test_helper"

module ShopifyAPITest
  module Auth
    class OauthCookiePredictabilityTest < Test::Unit::TestCase
      def test_offline_session_cookie_value_has_no_mac_and_equals_predictable_string
        shop = "victim-shop.myshopify.com"

        # Attacker-computable value using only public info (the shop domain).
        forged_value = ShopifyAPI::Utils::SessionUtils.offline_session_id(shop)

        session = ShopifyAPI::Auth::Session.new(id: forged_value, shop: shop, access_token: "real-token")
        cookie = ShopifyAPI::Auth::Oauth::SessionCookie.new(value: session.id, expires: nil)

        # Binding under test: cookie.value is byte-for-byte identical to the
        # unsigned, deterministic string, with no MAC field anywhere on SessionCookie.
        assert_equal(forged_value, cookie.value)
        assert_equal("offline_#{shop}", cookie.value)
        refute_respond_to(cookie, :hmac)
        refute_respond_to(cookie, :signature)

        # Attacker never sees the real cookie; they forge it directly and it is
        # accepted by current_session_id exactly like the legitimate one.
        forged_cookies = { ShopifyAPI::Auth::Oauth::SessionCookie::SESSION_COOKIE_NAME => forged_value }
        ShopifyAPI::Context.stubs(:embedded?).returns(false)

        recovered_id = ShopifyAPI::Utils::SessionUtils.current_session_id(nil, forged_cookies, false)
        assert_equal(session.id, recovered_id) # attacker-forged ID == real session ID
      end
    end
  end
end
```

### Citations

**File:** lib/shopify_api/auth/oauth/session_cookie.rb (L7-24)
```ruby
      class SessionCookie < T::Struct
        extend T::Sig

        SESSION_COOKIE_NAME = "shopify_app_session"

        const :name, String, default: SESSION_COOKIE_NAME
        const :value, String
        const :expires, T.nilable(Time)

        alias_method :eql?, :==
        sig { params(other: T.nilable(SessionCookie)).returns(T::Boolean) }
        def ==(other)
          return false unless other

          name == other.name &&
            value == other.value &&
            expires == other.expires
        end
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

**File:** lib/shopify_api/utils/session_utils.rb (L63-66)
```ruby
        sig { params(shop: String).returns(String) }
        def offline_session_id(shop)
          "offline_#{shop}"
        end
```
