### Title
Predictable, unsigned session cookie value enables cross-tenant session/access-token retrieval - ([File: lib/shopify_api/utils/session_utils.rb], [File: lib/shopify_api/auth/session.rb], [File: lib/shopify_api/auth/oauth/session_cookie.rb])

### Summary
The identity binding that should hold is: `session_id_returned_by_the_gem == session_id_that_is_cryptographically_bound_to_the_requesting_shop`. In this gem, that binding does not exist: session IDs are deterministic, guessable strings, and the cookie that carries them is a plain, unsigned value that `SessionUtils` trusts verbatim to key the session store (and thus the merchant's access token).

### Finding Description
When a session is created after OAuth, its `id` is generated deterministically from the shop domain: `"offline_#{shop}"` for offline sessions or `"#{shop}_#{associated_user.id}"` for online sessions. [1](#0-0) 

This id is placed, as plain text, directly into the response cookie with no signature, encryption, or any other integrity binding: [2](#0-1) [3](#0-2) 

On subsequent requests, `SessionUtils.current_session_id` — for non-embedded apps, or as the embedded fallback when no JWT is present — reads this cookie value back out and returns it unmodified as the session id to be used for loading the session (and its access token) from the host app's session storage: [4](#0-3) [5](#0-4) 

No check is performed anywhere in this path that the cookie's value actually belongs to, or was ever issued for, the shop/tenant making the current request. Contrast this with the JWT-based path (`session_id_from_shopify_id_token`), where the shop claim is bound inside an HS256-signed token verified against `Context.api_secret_key`: [6](#0-5) [7](#0-6) 

The cookie-based fallback has no equivalent binding: the "bytes verified" (none — the cookie is read as-is) do not match the "bytes that should have been cryptographically bound" (a signature over shop+id analogous to the JWT `aud`/`dest` claims).

### Impact Explanation
Because the session id format `offline_{shop}.myshopify.com` (or `{shop}_{user_id}`) is fully deterministic and the shop domain of any Shopify store is public information (it's part of every store's URL), any unprivileged user who can install the app on their own store (attacker's tenant) can trivially construct the exact session-id string for a victim merchant's tenant and set it as the value of `shopify_app_session` in their own browser session. If the host application follows this gem's documented API (`SessionUtils.current_session_id` → `SessionStorage.load_session(id)`), it will hand back the victim's `Session` object, including the victim shop's `access_token`, to the attacker. This is cross-tenant access to another merchant's access token — a Critical-severity impact per the stated criteria.

### Likelihood Explanation
Likelihood is high in any non-embedded deployment (or embedded deployment falling back to cookies, e.g., no `Authorization: Bearer <jwt>` header present) because: (1) no secret or privileged credential is required by the attacker, (2) the session id is derived from public data (the shop's `myshopify.com` domain) with a fixed, documented naming scheme, and (3) the vulnerable code path (`cookie_session_id`) is the gem's own documented mechanism for resolving the current session, not a misuse of the API by the host app.

### Recommendation
Do not use a raw, predictable, unsigned session id as the sole cookie value. Either (a) sign the cookie value (e.g., HMAC it with `Context.api_secret_key`, verifying it in `current_session_id`/`cookie_session_id` the same way `HmacValidator` is used for OAuth callbacks), or (b) use an unguessable, randomly generated identifier (e.g., `SecureRandom.uuid`, already available via `Session#id`'s default) as the cookie value instead of the deterministic `offline_#{shop}` / `#{shop}_#{user_id}` string, and only use the deterministic string as an internal storage key that is never exposed to the client.

### Proof of Concept
1. Attacker installs the app on their own store `attacker-shop.myshopify.com` and completes OAuth normally, learning that the resulting cookie value format is `offline_attacker-shop.myshopify.com`.
2. Attacker identifies a victim merchant's storefront (e.g. via the storefront URL or app listing) as `victim-shop.myshopify.com`.
3. Attacker manually sets their browser's `shopify_app_session` cookie to `offline_victim-shop.myshopify.com` and issues a request to the host application.
4. The host app calls `ShopifyAPI::Utils::SessionUtils.current_session_id(nil, cookies, false)`, which returns `"offline_victim-shop.myshopify.com"` unchanged [8](#0-7) , and the host app's `SessionStorage.load_session` returns the victim's stored `Session`, including `access_token`, to the attacker.

### Citations

**File:** lib/shopify_api/auth/session.rb (L111-117)
```ruby
          if is_online
            associated_user = T.must(access_token_response.associated_user)
            associated_user_scope = access_token_response.associated_user_scope
            id = "#{shop}_#{associated_user.id}"
          else
            id = "offline_#{shop}"
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

**File:** lib/shopify_api/auth/oauth/session_cookie.rb (L7-14)
```ruby
      class SessionCookie < T::Struct
        extend T::Sig

        SESSION_COOKIE_NAME = "shopify_app_session"

        const :name, String, default: SESSION_COOKIE_NAME
        const :value, String
        const :expires, T.nilable(Time)
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

**File:** lib/shopify_api/utils/session_utils.rb (L68-71)
```ruby
        sig { params(cookies: T::Hash[String, String]).returns(T.nilable(String)) }
        def cookie_session_id(cookies)
          cookies[Auth::Oauth::SessionCookie::SESSION_COOKIE_NAME]
        end
```

**File:** lib/shopify_api/auth/jwt_payload.rb (L24-45)
```ruby
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
