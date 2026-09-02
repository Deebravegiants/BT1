### Title
Non-embedded/cookie-based session lookup trusts an unsigned session identifier - (File: `lib/shopify_api/utils/session_utils.rb`)

### Summary
`ShopifyAPI::Utils::SessionUtils.current_session_id` derives the session identifier for non-embedded apps (and as a fallback for embedded apps) directly from the raw value of the `shopify_app_session` cookie, with no cryptographic verification binding that value to a real, completed OAuth flow. This is functionally the same bug class as the report's "trusting attacker-controlled input to short-circuit an identity/progression check": here, a "session id derived from unauthenticated bytes" is used to fetch and activate a merchant's stored access token.

### Finding Description
For the JWT-based (embedded) path, `session_id_from_shopify_id_token` builds the session id only after the token has passed cryptographic verification in `Auth::JwtPayload` (HMAC-SHA256 signature check against `Context.api_secret_key`, plus `aud` binding): [1](#0-0) [2](#0-1) 

For the cookie-based (non-embedded, or embedded-without-id-token) path, however, `cookie_session_id` simply returns whatever byte string is stored in the `shopify_app_session` cookie, with **no signature, no HMAC, and no re-derivation from a verified source**: [3](#0-2) [4](#0-3) 

That cookie's value is populated once, at the end of OAuth, directly from `session.id` (predictable, well-known formats such as `offline_{shop}` or `{shop}_{user_id}` per `jwt_session_id`/`offline_session_id`): [5](#0-4) [6](#0-5) 

The gem's own `SessionCookie` object carries only `name`, `value`, and `expires` — there is no signature/MAC field to tie the cookie's value back to the OAuth transaction that created it: [7](#0-6) 

And the gem's own documented integration pattern stores this value as a plain (non-signed) browser cookie, protected only by `secure`/`http_only` flags — never any cryptographic binding: [8](#0-7) 

The broken identity binding, stated as an equality that should hold but doesn't:
`session_id_used_to_load_credentials == session_id_produced_by_a_verified_OAuth_completion_for_that_shop`

In the cookie path, the left side is just `cookies["shopify_app_session"]` — arbitrary, attacker-settable bytes in the caller's own browser context — with no check that it was ever actually issued by this gem's `validate_auth_callback` for the shop it claims to represent.

### Impact Explanation
Because session ids follow a fixed, guessable pattern (`offline_{shop_domain}` for offline tokens, `{shop_domain}_{user_id}` for online tokens) and `shop_domain` values are public (they're literally the merchant's `myshopify.com` storefront hostname), an attacker who can set/inject this specific cookie value in their own browser (e.g. any user of a shared/multi-tenant host domain, a related subdomain, an XSS on a co-hosted page, or simply a host app that echoes/accepts a client-supplied cookie without additional integrity protection) can cause `SessionUtils.current_session_id` to return the id of a session belonging to a **different shop**. If the host application's session store contains that shop's persisted `access_token` (which it will, once that shop has completed OAuth), the caller's request is then serviced using another merchant's access token — cross-tenant account/session takeover, without ever presenting valid Shopify-issued credentials for the shop being impersonated.

### Likelihood Explanation
Medium: exploitation depends on the host application's cookie handling (e.g., cookie scope, XSS, or a session-store keyed purely by this predictable string), which is outside this gem's direct control, but the gem itself provides zero cryptographic verification for this specific, documented flow (`cookie_session_id`) — unlike the equivalent JWT-based lookup, which is fully verified. Any host application following the gem's own documented pattern inherits this gap.

### Recommendation
Bind the session cookie's value to a value that cannot be forged/guessed by a third party (e.g., a cryptographically random session key that is separately mapped, server-side, to the actual `shop`/`access_token`, rather than a client-controlled, human-readable, and predictable `shop`-derived string), or sign/HMAC the cookie value the same way the OAuth callback query is HMAC-validated, and verify that signature in `SessionUtils.cookie_session_id` before trusting it to load a session.

### Proof of Concept
1. Merchant A completes OAuth for `shop-a.myshopify.com`; the gem sets the browser cookie `shopify_app_session = offline_shop-a.myshopify.com` (per `Session.from` + `SessionCookie.new(value: session.id, ...)` in `oauth.rb`).
2. Attacker knows (or guesses) that shop `victim-shop.myshopify.com` also has the app installed (public knowledge — it's the storefront domain).
3. Attacker sets their own browser's `shopify_app_session` cookie to `offline_victim-shop.myshopify.com` and issues a request to the host app.
4. `SessionUtils.current_session_id` → `cookie_session_id` returns `"offline_victim-shop.myshopify.com"` verbatim, with no verification: [4](#0-3) 
5. The host application looks up this id in its session store, retrieves `victim-shop`'s persisted access token, and services the attacker's request using it — cross-tenant access achieved with no Shopify-verified credential for `victim-shop`.

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

**File:** lib/shopify_api/auth/jwt_payload.rb (L23-45)
```ruby
      sig { params(token: String).void }
      def initialize(token)
        payload_hash = begin
          decode_token(token, Context.api_secret_key)
        rescue ShopifyAPI::Errors::InvalidJwtTokenError
          raise unless Context.old_api_secret_key

          decode_token(token, T.must(Context.old_api_secret_key))
        end

        @iss = T.let(payload_hash["iss"], String)
        @dest = T.let(payload_hash["dest"], String)
        @aud = T.let(payload_hash["aud"], String)
        @sub = T.let(payload_hash["sub"], T.nilable(String))
        @exp = T.let(payload_hash["exp"], Integer)
        @nbf = T.let(payload_hash["nbf"], Integer)
        @iat = T.let(payload_hash["iat"], Integer)
        @jti = T.let(payload_hash["jti"], String)
        @sid = T.let(payload_hash["sid"], T.nilable(String))

        raise ShopifyAPI::Errors::InvalidJwtTokenError,
          "Session token had invalid API key" unless @aud == Context.api_key
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

**File:** docs/usage/oauth.md (L253-259)
```markdown
    # Update cookies with the authorized access token from result
    cookies[auth_result[:cookie].name] = {
      expires: auth_result[:cookie].expires,
      secure: true,
      http_only: true,
      value: auth_result[:cookie].value
    }
```
