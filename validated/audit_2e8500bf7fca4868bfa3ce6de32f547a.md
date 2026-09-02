### Title
Predictable, Unsigned Session Identifier Used as Session-Cookie Value Enables Session Fixation / Cross-Tenant Session Hijacking - ([File: lib/shopify_api/auth/session.rb])

### Summary
For non-embedded (and embedded-fallback) app flows, the gem sets the browser's session cookie value to the exact same string that is used as the session-storage lookup key. This identifier is not a random secret — it is deterministically derived from public information (the shop domain and, for online sessions, the associated user id). Anyone who knows or can guess these values can construct the valid session-cookie value for a victim shop/user without needing the app's `client_secret`, an access token, or any signature, breaking the intended binding "authenticated bytes == session identity."

### Finding Description
When OAuth completes, `Session.from` builds the session `id` as a plain deterministic string:
- online: `"#{shop}_#{associated_user.id}"`
- offline: `"offline_#{shop}"` [1](#0-0) 

`Auth::Oauth.validate_auth_callback` then uses this same predictable `session.id` as the value of the `shopify_app_session` cookie for non-embedded apps: [2](#0-1) 

Later, `Utils::SessionUtils.current_session_id` reads this cookie value back verbatim and treats it as the authenticated session id, with no cryptographic check that the presented cookie value was actually issued by the server for that browser: [3](#0-2) [4](#0-3) 

Contrast this with the embedded/JWT path, where the session id is only accepted after `Auth::JwtPayload` verifies an HMAC-signed token (`JWT.decode(... true, algorithm: "HS256")`) bound to `Context.api_secret_key`: [5](#0-4) 

The cookie-based path has no analogous integrity check: `cookie_session_id` simply returns whatever value is in the cookie. Because that value is fully predictable from public data (shop domain, user id), the "identity binding" that the cookie is supposed to enforce — *presented session id == the session id the server actually issued to this browser after OAuth* — is broken. This mirrors the report's root cause: a consumer (`current_session_id`/session storage) trusts a value's shape/content as if it were authenticated, while the producer (`validate_auth_callback`) emitted a value that carries no authentication of its own, only reused a lookup key as if it were a credential.

### Impact Explanation
An unprivileged internet user who knows a target shop's `myshopify.com` domain (public) and, for online sessions, the associated Shopify staff user id (often discoverable or brute-forceable, e.g., low sequential ids) can construct the exact `shopify_app_session` cookie value the app would issue for that shop/user. By setting this cookie in their own browser before or in place of a legitimate session lookup, they can cause the host app to resolve to the victim's stored session (and thus its access token) — cross-tenant session access — or perform session fixation by pre-setting the cookie in a victim's browser prior to OAuth completion. This satisfies the High-impact category "session fixation or forced OAuth completion" / cross-tenant access, achieved purely through this gem's own session-id construction and cookie-consumption logic, without needing `api_secret_key`, an access token, or TLS interception.

### Likelihood Explanation
Exploitability depends on the host app relying on the gem's documented `current_session_id`/cookie flow (the non-embedded default) and on the attacker being able to guess/know the associated user id or targeting an offline session (where the id is purely `offline_{shop}`, needing no guessing at all). The offline-session case requires no secret information beyond the shop domain, making it directly reachable by any internet user who knows a target's store domain.

### Recommendation
Do not reuse the internal session-storage key as the externally-facing cookie value. Issue a cryptographically random, unguessable session-cookie value (e.g., `SecureRandom.uuid`/`SecureRandom.hex`) that is mapped server-side to the real session id, analogous to how `SessionCookie` already uses `SecureRandom.alphanumeric(NONCE_LENGTH)` for the OAuth `state` nonce. Alternatively, sign/HMAC the cookie value (similar to the JWT path) so that `cookie_session_id` can verify authenticity before trusting it as a session key.

### Proof of Concept
1. Determine or guess a target store's domain, e.g. `victim-shop.myshopify.com` (public).
2. For the offline-session case, compute the predictable session id: `offline_victim-shop.myshopify.com` (per `Session.from`, `lib/shopify_api/auth/session.rb:116`).
3. Set the browser cookie `shopify_app_session=offline_victim-shop.myshopify.com` and request an app endpoint that calls `Utils::SessionUtils.current_session_id` → `cookie_session_id`.
4. The host app looks up the session store using this attacker-supplied, unauthenticated value and, if a session with that id exists (created during the shop's own legitimate install), the attacker's request is now associated with the victim shop's session/access token — no `client_secret`, access token, or JWT signing key was ever needed.

### Citations

**File:** lib/shopify_api/auth/session.rb (L107-117)
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

**File:** lib/shopify_api/utils/session_utils.rb (L68-71)
```ruby
        sig { params(cookies: T::Hash[String, String]).returns(T.nilable(String)) }
        def cookie_session_id(cookies)
          cookies[Auth::Oauth::SessionCookie::SESSION_COOKIE_NAME]
        end
```

**File:** lib/shopify_api/auth/jwt_payload.rb (L76-81)
```ruby
      sig { params(token: String, api_secret_key: String).returns(T::Hash[String, T.untyped]) }
      def decode_token(token, api_secret_key)
        JWT.decode(token, api_secret_key, true, leeway: JWT_LEEWAY, algorithm: "HS256")[0]
      rescue JWT::DecodeError => err
        raise ShopifyAPI::Errors::InvalidJwtTokenError, "Error decoding session token: #{err.message}"
      end
```
