### Title
Cookie-derived offline/online session IDs are unauthenticated and fully predictable, enabling cross-tenant session/access-token theft - ([File: lib/shopify_api/utils/session_utils.rb])

### Summary
`ShopifyAPI::Utils::SessionUtils.current_session_id` derives the session lookup key for non-embedded apps directly from the raw `shopify_app_session` browser cookie value, with no cryptographic binding to a Shopify-issued credential. Session IDs are deterministic and guessable (`"offline_#{shop}"` or `"#{shop}_#{user_id}"`), so any unprivileged client can set this cookie to an arbitrary value and cause a host app to look up and act on another shop's stored session/access token.

### Finding Description
For non-embedded apps, `SessionCookie` is set after OAuth to the plain, unsigned `session.id` value: [1](#0-0) 

`Session.id` (and the offline/online variants) are fully deterministic strings derived only from the `shop` domain and, for online sessions, the numeric `associated_user.id`: [2](#0-1) 

`SessionCookie` itself carries no signature, MAC, or encryption — it is a plain `name`/`value`/`expires` struct: [3](#0-2) 

When retrieving the "current session," `SessionUtils.current_session_id` for non-embedded apps (and as a fallback for embedded apps without a JWT) simply reads this cookie value back out and returns it as the session ID with **no verification whatsoever**: [4](#0-3) [5](#0-4) 

This contrasts sharply with the embedded-app / JWT path, where the session ID is only ever derived from claims inside a cryptographically verified JWT (`Auth::JwtPayload.new(id_token)` validates the HS256 signature against `Context.api_secret_key` before `shop`/`sub` are trusted): [6](#0-5) [7](#0-6) 

The documented usage pattern in this gem explicitly tells non-embedded apps to pass raw request cookies into `current_session_id` to obtain the ID used to retrieve the stored `Session`/access token from app storage: [8](#0-7) 

**Identity binding broken:** the equality the library should enforce is `session_id returned to caller == session_id cryptographically attested by Shopify for the caller's actual shop/session`. Instead, the library enforces only `session_id returned to caller == bytes sent by the client in an arbitrary cookie`. Because the ID format is public and deterministic (`offline_<shop>.myshopify.com`, `<shop>.myshopify.com_<user_id>`), an unprivileged internet user can set `Cookie: shopify_app_session=offline_victim-shop.myshopify.com` on a request to the host application and have `current_session_id` hand back that exact string, which the host app is instructed by this gem's own documented pattern to use as the lookup key into its session store — retrieving the victim shop's stored access token.

### Impact Explanation
If the host application follows this gem's documented, recommended pattern (cookie → `current_session_id` → `SessionRepository.retrieve_session(id)` → use returned `Session.access_token` for API calls), an unauthenticated attacker who merely knows or guesses a victim shop's domain (shop domains are not secret) can obtain that shop's `Session` object and its Shopify Admin `access_token` from the host app's storage — a cross-tenant access-token theft entirely mediated by primitives this gem provides and documents (`SessionCookie`, `SessionUtils.current_session_id`). This meets the Critical bar: theft/exfiltration of a merchant access token and cross-tenant access.

### Likelihood Explanation
High for any non-embedded app built following the gem's own documented cookie flow: no secret, prior session, or MITM capability is required — only the ability to set an arbitrary cookie value in a request to the app (trivial for any web client) and knowledge of the target's `myshopify.com` domain, which is public. The online-session ID additionally requires the numeric Shopify user id, which is also often discoverable/enumerable, but the offline (store-level) session ID requires only the shop domain.

### Recommendation
Do not use the raw session ID as an unauthenticated cookie value. Sign/HMAC the cookie value (or store an opaque, unguessable random token server-side, e.g. `SecureRandom.uuid`, and map it internally to the deterministic session ID) so that `SessionUtils.cookie_session_id`/`current_session_id` can verify the cookie was actually issued by this app for the corresponding OAuth flow before trusting it as a lookup key, mirroring the integrity guarantee already provided on the embedded/JWT path.

### Proof of Concept
1. App owner installs a Storj-analogous non-embedded Shopify app on `victim-shop.myshopify.com`; the gem sets cookie `shopify_app_session=offline_victim-shop.myshopify.com` (per `lib/shopify_api/auth/oauth.rb` lines 100-110).
2. Attacker, with no credentials, sends a request to the host app with header `Cookie: shopify_app_session=offline_victim-shop.myshopify.com`.
3. Host app calls `ShopifyAPI::Utils::SessionUtils.current_session_id(nil, cookies, false)` as documented in `docs/getting_started.md` (lines 47-52); the raw cookie value is returned unmodified.
4. Host app looks up `SessionRepository.retrieve_session("offline_victim-shop.myshopify.com")` and uses the returned `Session#access_token` to make Admin API calls on the attacker's behalf against `victim-shop`.

### Citations

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

**File:** lib/shopify_api/auth/session.rb (L107-118)
```ruby
        sig { params(shop: String, access_token_response: Oauth::AccessTokenResponse).returns(Session) }
        def from(shop:, access_token_response:)
          is_online = access_token_response.online_token?

          if is_online
            associated_user = T.must(access_token_response.associated_user)
            associated_user_scope = access_token_response.associated_user_scope
            id = "#{shop}_#{associated_user.id}"
          else
            id = "offline_#{shop}"
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

**File:** docs/getting_started.md (L47-52)
```markdown
#### Cookie
Cookie based authentication is not supported for embedded apps due to browsers dropping support for third party cookies due to security concerns. Non-embedded apps are able to use cookies for session storage/retrieval.

For *non-embedded* apps, you can pass the cookies into:
 - `ShopifyAPI::Utils::SessionUtils.current_session_id(nil, cookies, true)` for online (user) sessions or
 - `ShopifyAPI::Utils::SessionUtils.current_session_id(nil, cookies, false)` for offline (store) sessions.
```
