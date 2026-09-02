### Title
Non-embedded session identity is a bare, unsigned session ID trusted directly from the cookie - cross-tenant session hijacking via predictable session IDs (`lib/shopify_api/utils/session_utils.rb`)

### Summary
For non-embedded apps (and as a fallback for embedded apps), `ShopifyAPI::Utils::SessionUtils.current_session_id` treats the raw, unsigned session cookie value as the trusted session identifier with no cryptographic binding proving the browser actually completed OAuth for that session.

### Finding Description
`SessionUtils.current_session_id` reads the session identifier directly out of the cookie jar and returns it as-is for lookup by the host app's session storage: [1](#0-0) [2](#0-1) 

The cookie value that gets trusted here is nothing more than `session.id`, set directly (unsigned, unencrypted) when OAuth completes: [3](#0-2) 

Session IDs are deterministic and derived entirely from public information — the shop's `myshopify.com` domain (and, for online sessions, a user id): [4](#0-3) [5](#0-4) 

The identity binding that is broken: `cookie value == session lookup key`, with no HMAC or signature tying the cookie to the specific session it was minted for. Because the ID format (`offline_{shop}` or `{shop}_{user_id}`) is fully predictable from a publicly-known shop domain, any unprivileged internet user who knows (or guesses) a target merchant's `*.myshopify.com` domain can construct the exact same string an authenticated session would use as its cookie value.

### Impact Explanation
If an attacker can get their forged cookie value accepted by the host application's session store (e.g. by setting it in their own browser, or via any mechanism that lets them influence the cookie for a request to the app, such as subdomain cookie scoping or lack of `Secure`/`SameSite` protections upstream), the app will resolve and activate the victim shop's real, already-issued offline access token session — a cross-tenant session hijack with no credential required. This matches the "Critical — cross-tenant access" impact bucket, since the actual `access_token` bound to that session is used on the attacker's behalf.

### Likelihood Explanation
Likelihood depends on the host app's cookie handling and session storage semantics, which are outside this gem, but the gem itself provides no defense: it neither signs the session cookie nor binds it via HMAC to the actual OAuth completion, and the ID space is fully predictable from a shop domain that is often public (e.g. visible in storefront URLs, app listings, etc.). No secret, access token, or privileged position is required to construct the forged identifier itself.

### Recommendation
- Do not use the raw, predictable `session.id` as the cookie value that determines the "current session." Use a random, unguessable, unrelated session token, and let host applications map that opaque token to the underlying `Session` object server-side.
- Alternatively, HMAC-sign the cookie value using `Context.api_secret_key` so a value cannot be forged without knowledge of the secret, and validate that signature in `SessionUtils.cookie_session_id`.

### Proof of Concept
1. Attacker learns/guesses a merchant's shop domain, e.g. `victim-store.myshopify.com` (publicly discoverable via the storefront, app directory, etc.).
2. Attacker computes the deterministic offline session id: `offline_victim-store.myshopify.com` (per `Utils::SessionUtils.offline_session_id`).
3. Attacker sets this value as the `shopify_app_session` cookie (per `SessionCookie::SESSION_COOKIE_NAME`) on a request to the target Rails/Sinatra app built on this gem.
4. `SessionUtils.current_session_id` returns this attacker-supplied string unchanged (`cookie_session_id`), and if the host's `SessionRepository` looks up sessions purely by this ID (the pattern this gem's docs encourage), the app activates the victim's real, already-authorized `Session` (including its `access_token`) for the attacker's request — cross-tenant session hijacking without any credential.

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

**File:** lib/shopify_api/auth/oauth.rb (L100-112)
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

          { session: session, cookie: cookie }
```

**File:** lib/shopify_api/auth/session.rb (L107-140)
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

          if access_token_response.expires_in
            expires = Time.now + access_token_response.expires_in.to_i
          end

          if access_token_response.refresh_token_expires_in
            refresh_token_expires = Time.now + access_token_response.refresh_token_expires_in.to_i
          end

          new(
            id: id,
            shop: shop,
            access_token: access_token_response.access_token,
            scope: access_token_response.scope,
            is_online: is_online,
            associated_user_scope: associated_user_scope,
            associated_user: associated_user,
            expires: expires,
            shopify_session_id: access_token_response.session,
            refresh_token: access_token_response.refresh_token,
            refresh_token_expires: refresh_token_expires,
          )
        end
```
