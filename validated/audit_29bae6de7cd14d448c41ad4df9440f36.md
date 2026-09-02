### Title
Predictable, unsigned session cookie value lets an attacker guess and hijack another shop's persisted session - (File: lib/shopify_api/utils/session_utils.rb)

### Summary
`SessionUtils.current_session_id` returns the raw `shopify_app_session` cookie value verbatim as the session identifier, with no MAC, signature, or shop-binding check. Because the gem itself generates this identifier deterministically from the shop domain (`offline_#{shop}` or `#{shop}_#{user_id}`) and writes it into the cookie in plaintext during `Oauth.validate_auth_callback`, an attacker who knows (or guesses) a victim shop's `.myshopify.com` domain can construct the exact session id string themselves and present it as their own cookie value to hijack the lookup for that shop's persisted session.

### Finding Description
The invariant that should hold is: **shop authenticated by signature/JWT == shop interpolated into the session id == shop used as the request host**. This holds in the embedded/JWT path, where `session_id_from_shopify_id_token` derives the shop strictly from a JWT verified against `Context.api_secret_key` [1](#0-0) . It does **not** hold in the cookie path.

`cookie_session_id` simply returns whatever is in the `shopify_app_session` cookie with no verification at all: [2](#0-1) 
This is reached for every non-embedded app request, and as a fallback for embedded apps without a JWT: [3](#0-2) 

The value originally placed in this cookie by the gem is not a random opaque token — it is deterministically derived from the shop domain by `Oauth.validate_auth_callback`, which sets the plaintext cookie value directly to `session.id`: [4](#0-3) 
and the id formats are public, guessable string constructions: [5](#0-4) 

Since a shop's `.myshopify.com` domain is public, `offline_#{shop}` is fully derivable by anyone without ever observing a real cookie. The `SessionCookie` struct carries no MAC/expiry-binding of its own [6](#0-5) , and the gem's own docs instruct developers to store this value as a plain cookie (`secure`/`http_only` only, not `cookies.signed`/`cookies.encrypted`), reinforcing the unsigned usage pattern [7](#0-6) .

Attacker request: send any HTTP request to the target app with header `Cookie: shopify_app_session=offline_victim-shop.myshopify.com`. `current_session_id(nil, cookies, false)` returns `"offline_victim-shop.myshopify.com"` unmodified — confirmed by the existing test `test_non_embedded_app_current_session_id_returns_id_from_cookie`, which shows any arbitrary cookie value is returned as-is [8](#0-7) . If the host app's session storage (keyed by this same deterministic id, per the gem's documented usage) already has a persisted offline session for `victim-shop.myshopify.com` (i.e., the shop previously installed the app), the host app will load and use the victim's real `access_token` to service the attacker's request — no HMAC, no JWT, no secret ever touched by the attacker.

No existing guard in this gem prevents this: `HmacValidator.validate` and the `state` check only protect the one-time OAuth callback exchange, not subsequent cookie-based session lookups; `JwtPayload`'s `aud`/`iss` checks only apply to the embedded JWT path, which is bypassed entirely once a cookie is presented; `Context.setup?`/`private?`/`embedded?` gate configuration, not per-request shop binding; Sorbet only checks types, not values.

### Impact Explanation
An attacker with zero credentials can cause the host app to treat a request as authenticated for an arbitrary victim shop merely by knowing that shop's domain, using the victim's real, previously-issued offline access token to serve the attacker's request. This is cross-tenant access: the attacker's request operates with another tenant's authenticated identity and, transitively, their access token's privileges, matching the Critical "cross-tenant access" / "authentication bypass" category. It is repeatable against any shop whose domain is known and who has installed the app, with no per-victim secret needed and no rate limit consideration in scope.

### Likelihood Explanation
Preconditions: the host app must be non-embedded (or an embedded app that falls back to cookie auth) and must use the session id purely as a storage lookup key without any additional per-request shop/host binding check — which is exactly what this gem's own documentation instructs. Attacker cost is trivial: knowledge of the target's `.myshopify.com` domain (offline sessions are singular per shop and their id is derived purely from that domain) and the ability to set an HTTP `Cookie` header, which every unprivileged internet client can do. No XSS, MITM, or secret is required.

### Recommendation
Do not return raw, unsigned, developer-supplied cookie values as trusted session identifiers. Either (a) require the host app to store session ids as `cookies.signed`/`cookies.encrypted` (and document this as mandatory, not optional) so the value cannot be forged or guessed, or (b) generate a cryptographically random opaque session cookie value (unrelated to `shop`/`user_id`) inside `SessionUtils`/`Oauth`, and bind the actual `shop` only via the server-side session record looked up by that opaque id, never trusting a shop the client can influence.

### Proof of Concept
```ruby
# test/utils/session_utils_test.rb (illustrative addition)
def test_cookie_session_id_accepts_arbitrary_unsigned_value
  ShopifyAPI::Context.stubs(:embedded?).returns(false)
  forged_cookie_value = "offline_victim-shop.myshopify.com"
  cookies = { ShopifyAPI::Auth::Oauth::SessionCookie::SESSION_COOKIE_NAME => forged_cookie_value }

  returned_id = ShopifyAPI::Utils::SessionUtils.current_session_id(nil, cookies, false)

  # No MAC/shop-binding check occurred: attacker-chosen string returned verbatim,
  # identical to the id the gem itself would generate for the real victim shop.
  assert_equal(forged_cookie_value, returned_id)
  assert_equal(ShopifyAPI::Utils::SessionUtils.offline_session_id("victim-shop.myshopify.com"), returned_id)
end
```
This demonstrates that `current_session_id` performs no cryptographic validation and returns a fully attacker-guessable identifier matching the format the gem itself uses for real victim sessions.

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

**File:** lib/shopify_api/utils/session_utils.rb (L45-56)
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
```

**File:** lib/shopify_api/utils/session_utils.rb (L58-66)
```ruby
        sig { params(shop: String, user_id: String).returns(String) }
        def jwt_session_id(shop, user_id)
          "#{shop}_#{user_id}"
        end

        sig { params(shop: String).returns(String) }
        def offline_session_id(shop)
          "offline_#{shop}"
        end
```

**File:** lib/shopify_api/utils/session_utils.rb (L68-71)
```ruby
        sig { params(cookies: T::Hash[String, String]).returns(T.nilable(String)) }
        def cookie_session_id(cookies)
          cookies[Auth::Oauth::SessionCookie::SESSION_COOKIE_NAME]
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

**File:** lib/shopify_api/auth/oauth/session_cookie.rb (L7-25)
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
      end
```

**File:** docs/usage/oauth.md (L186-200)
```markdown

    # Store the authorization cookie
    cookies[auth_response[:cookie].name] = {
      expires: auth_response[:cookie].expires,
      secure: true,
      http_only: true,
      value: auth_response[:cookie].value
    }

    # Redirect the user to "auth_response[:auth_route]" to allow user to grant the app permission
    # This will lead the user to the Shopify Authorization page
    head 307
    response.set_header("Location", auth_response[:auth_route])
  end
end
```

**File:** test/utils/session_utils_test.rb (L80-89)
```ruby
      def test_non_embedded_app_current_session_id_returns_id_from_cookie
        ShopifyAPI::Context.stubs(:embedded?).returns(false)
        expected_session_id = "cookie_value"
        cookies = { ShopifyAPI::Auth::Oauth::SessionCookie::SESSION_COOKIE_NAME => expected_session_id }

        assert_equal(
          expected_session_id,
          ShopifyAPI::Utils::SessionUtils.current_session_id(nil, cookies, true),
        )
      end
```
