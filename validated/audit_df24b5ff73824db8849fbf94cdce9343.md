### Title
Unauthenticated, attacker-guessable `Cookie: shopify_app_session=<id>` value is trusted as an authenticated session identifier, bypassing JWT verification for embedded apps - (File: `lib/shopify_api/utils/session_utils.rb`)

### Summary
`SessionUtils.current_session_id` only verifies identity via `Auth::JwtPayload` when a `shopify_id_token` is present. When it is omitted, the `else` branch at [1](#0-0)  falls straight through to `cookie_session_id`, which returns the raw, unverified value of the `shopify_app_session` cookie as the session id, with zero cryptographic binding to any authenticated caller.

### Finding Description
The equality the code implicitly relies on is: `session_id returned by current_session_id == the session id of the shop that legitimately owns this request`. The JWT path enforces this by verifying `Auth::JwtPayload` (`iss`/`dest`/`aud`/`sub`) before deriving `jwt_session_id`/`offline_session_id` at [2](#0-1) . The cookie fallback path performs no such check: `cookie_session_id` simply does `cookies[Auth::Oauth::SessionCookie::SESSION_COOKIE_NAME]` and returns it verbatim as the trusted session id [3](#0-2) . The `SessionCookie` struct that produces this value is a plain `T::Struct` with `name`, `value`, `expires` fields and no signing/MAC method [4](#0-3) .

Critically, the offline session id format is fully deterministic and derived only from public information: `offline_session_id(shop) = "offline_#{shop}"` [5](#0-4) . Since a shop's `myshopify.com` domain is public, any attacker can construct the exact cookie value for any target merchant (`offline_other-shop.myshopify.com`) without ever having obtained the real cookie, without holding `api_secret_key`, and without any JWT ever being verified. An attacker who calls the app directly (e.g. via curl/WebMock, not through a browser's same-origin cookie jar) simply omits `Authorization: Bearer <id_token>` and supplies the forged `Cookie` header; `Context.embedded?` is true, `shopify_id_token` is `nil`, so execution takes the `else` branch and returns the attacker-chosen id straight to the host app, which then looks up a real session (potentially containing another shop's access token) keyed by that id.

None of the documented guards apply here: `HmacValidator.validate` and `ShopValidator.sanitize!` are OAuth-callback-only checks; `JwtPayload`'s `aud`/`dest` checks never execute because `JwtPayload.new` is never invoked on this path; `HttpRequest#verify` is unrelated; `Context.embedded?` only selects the (vulnerable) branch, it doesn't validate the cookie's contents.

### Impact Explanation
If the host app trusts `current_session_id`'s return value to load a session from its `SessionStorage` and use `session.access_token` for Admin API calls (the exact intended usage per `docs/getting_started.md`), an attacker gains cross-tenant access: they can address any other merchant's stored offline session purely by knowing that merchant's `myshopify.com` domain, with no credential of their own. This is repeatable against any shop that has completed OAuth with the app, at essentially zero cost per attempt, and matches the "Critical - cross-tenant access" category.

### Likelihood Explanation
Preconditions: the app must be embedded (`Context.embedded? == true`, the default configuration for embedded apps using this gem) and must rely on the documented cookie fallback for cases where a JWT can't be supplied. The attacker needs only the target's `myshopify.com` domain, which is not secret. No API secret, access token, or victim interaction is required — the attacker directly issues the crafted HTTP request. This makes the attack cheap, deterministic, and fully repeatable against arbitrary victim shops that previously installed the app.

### Recommendation
Do not treat the raw `shopify_app_session` cookie value as a self-authenticating identifier. Either (a) sign/MAC the cookie value server-side (e.g., HMAC with a per-app secret) and verify the MAC in `cookie_session_id` before trusting it, or (b) bind the cookie to an independent, server-side session mechanism (e.g., Rack's encrypted/signed session cookie) rather than a bare, predictable string equal to `"offline_#{shop}"`, so that possession of the cookie — not knowledge of the shop domain — is what grants the session.

### Proof of Concept
```ruby
# test/utils/session_utils_test.rb (new test)
def test_cookie_fallback_accepts_forged_offline_session_id_without_jwt
  ShopifyAPI::Context.setup(..., is_embedded: true)

  forged_cookie = {
    ShopifyAPI::Auth::Oauth::SessionCookie::SESSION_COOKIE_NAME => "offline_other-shop.myshopify.com",
  }

  ShopifyAPI::Auth::JwtPayload.expects(:new).never

  session_id = ShopifyAPI::Utils::SessionUtils.current_session_id(nil, forged_cookie, false)

  assert_equal "offline_other-shop.myshopify.com", session_id
end
```
Assertions on both sides of the binding: (1) `Auth::JwtPayload.new` is never invoked (`expects(:new).never`), proving no identity verification occurred; (2) `session_id` equals the attacker-chosen `offline_other-shop.myshopify.com`, proving the returned identifier is fully attacker-controlled rather than tied to any verified caller — i.e. `session id returned` ≠ `shop authenticated by JWT` (the latter is undefined/never computed).

### Citations

**File:** lib/shopify_api/utils/session_utils.rb (L24-30)
```ruby
            else
              # falling back to session cookie
              raise Errors::CookieNotFoundError, "JWT token or Session cookie not found for app" unless
                cookies && cookies[Auth::Oauth::SessionCookie::SESSION_COOKIE_NAME]

              cookie_session_id(cookies)
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

**File:** lib/shopify_api/utils/session_utils.rb (L63-66)
```ruby
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
