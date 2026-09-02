### Title
Deterministic, unsigned offline session cookie enables cross-tenant session hijacking - (File: lib/shopify_api/utils/session_utils.rb)

### Summary
`Utils::SessionUtils.cookie_session_id` returns the raw `shopify_app_session` cookie value verbatim with no cryptographic verification, and that same value is deterministically derived from the public shop domain via `offline_session_id(shop) = "offline_#{shop}"`. An attacker who knows a target's public `.myshopify.com` domain can fabricate this cookie without ever installing the app, authenticating, or intercepting traffic, and the gem will hand back the exact identifier the host app's session storage uses to look up the victim's real offline access-token session.

### Finding Description
The claimed broken binding is: `session_id == cookies['shopify_app_session']`, with the implicit assumption elsewhere in the app that `session_id` was only ever set by this library after a successful, HMAC-validated OAuth callback (`Auth::Oauth.validate_auth_callback`, which does call `Utils::HmacValidator.validate(auth_query)` at [1](#0-0) ). That validation happens once, at token-exchange time, to produce a `SessionCookie` whose `value` is `session.id` [2](#0-1) . Critically, for non-embedded apps `session.id` is `offline_#{shop}` [3](#0-2)  — fully deterministic from the shop's public `.myshopify.com` domain, with no random or secret component.

`SessionCookie` itself is a plain `T::Struct` carrying only `name`, `value`, `expires` — no HMAC, no signature field [4](#0-3) . When the host app later reads the cookie back on a request, `current_session_id` for the non-embedded path (or the embedded fallback path) calls `cookie_session_id(cookies)`, which is a bare hash lookup with zero calls to `Context.api_secret_key` or any HMAC/JWT check: [5](#0-4)  and [6](#0-5) .

Attack: the attacker sends `GET /any-non-embedded-endpoint` with header `Cookie: shopify_app_session=offline_victim-shop.myshopify.com`. `Context.embedded?` is false, so `current_session_id` goes straight to `cookie_session_id`, returning `"offline_victim-shop.myshopify.com"` unchanged. The host app (per the documented pattern) then uses this string as the key into its session storage (`SessionStorage.load_session(session_id)`), which does hold a real record under that exact key — because the victim merchant's real offline session was created and persisted under `offline_#{shop}` during their legitimate install. The attacker never needed the victim's cookie, any secret, or any signature — only the victim's public shop domain.

None of the existing guards intervene here: `HmacValidator.validate` only runs once, during the OAuth callback that creates the session, not on every subsequent request that reads the cookie back; `ShopValidator.sanitize!` is not invoked on the cookie value in this path; the `state` comparison only guards the initial CSRF nonce during `begin_auth`/`validate_auth_callback`, not the post-auth session cookie; `JwtPayload`'s `aud` check is irrelevant to the non-JWT cookie fallback path; and `Context.embedded?`/`private?` merely select which branch runs — they do not add authentication to the cookie value itself.

### Impact Explanation
Any unprivileged attacker who knows a victim shop's `.myshopify.com` domain (always public — visible in any storefront URL) can construct the exact session-lookup key for that shop's persisted offline access-token session and have the host app's downstream logic (built exactly as documented) treat their request as an authenticated request for that shop. This is a cross-tenant access vulnerability: the attacker's unauthenticated HTTP request gets bound to another tenant's persisted access-token session with no proof of possession, no signature check, and no shop verification. It is trivially repeatable against arbitrary victim shops merely by changing the domain in the forged cookie, since `offline_#{shop}` requires no secret to compute.

### Likelihood Explanation
Preconditions are the gem's own standard, documented, non-embedded configuration (`Context.embedded?` returning false, which is the default configuration path shown in `docs/getting_started.md` for non-embedded apps) and a host app calling `current_session_id(nil, cookies, false)` as instructed. Attacker cost is a single crafted HTTP request with a guessed/known public shop domain — no credentials, no MITM, no social engineering, and no dependency on stealing an actual browser cookie. This is fully feasible and repeatable at scale against any shop that has installed the app.

### Recommendation
Do not use a deterministic, attacker-computable string (`offline_#{shop}`) as a bearer-equivalent session cookie value. Either (a) make the session cookie value a cryptographically random, unguessable token that is only mapped to `offline_#{shop}` server-side, or (b) sign/HMAC the cookie value using `Context.api_secret_key` and verify that signature in `cookie_session_id` before trusting it, mirroring the HMAC check already performed on OAuth callbacks and JWT tokens.

### Proof of Concept
```ruby
# test/utils/session_utils_test.rb (conceptual addition)
test "cookie_session_id trusts a forged deterministic offline session id with no signature check" do
  ShopifyAPI::Context.setup(
    api_key: "key", api_secret_key: "secret", api_version: "2024-01",
    is_private: false, is_embedded: false, host_name: "app.example.com",
  )

  forged_cookie_value = ShopifyAPI::Utils::SessionUtils.offline_session_id("victim-shop.myshopify.com")
  cookies = { "shopify_app_session" => forged_cookie_value }

  session_id = ShopifyAPI::Utils::SessionUtils.current_session_id(nil, cookies, false)

  assert_equal "offline_victim-shop.myshopify.com", session_id
  # No HmacValidator, no Context.api_secret_key usage, no signature verification occurred anywhere
  # in this call chain -- confirmed by reading lib/shopify_api/utils/session_utils.rb, which performs
  # only a plain Hash#[] lookup in cookie_session_id.
end
```

### Citations

**File:** lib/shopify_api/auth/oauth.rb (L64-64)
```ruby
          raise Errors::InvalidOauthError, "Invalid OAuth callback." unless Utils::HmacValidator.validate(auth_query)
```

**File:** lib/shopify_api/auth/oauth.rb (L105-110)
```ruby
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

**File:** lib/shopify_api/utils/session_utils.rb (L68-71)
```ruby
        sig { params(cookies: T::Hash[String, String]).returns(T.nilable(String)) }
        def cookie_session_id(cookies)
          cookies[Auth::Oauth::SessionCookie::SESSION_COOKIE_NAME]
        end
```

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
