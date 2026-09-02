### Title
Session cookie value is an unsigned, publicly-derivable session ID enabling cross-tenant session hijacking - ([File: lib/shopify_api/auth/oauth.rb])

### Summary
For non-embedded apps, `ShopifyAPI::Auth::Oauth.validate_auth_callback` sets the session cookie's value to the raw `session.id`, and `ShopifyAPI::Utils::SessionUtils.current_session_id`/`cookie_session_id` later trust that raw cookie value as the lookup key for the stored session. The session ID itself is not a secret or a signed/MAC'd token — it is deterministically derived from public data (the shop domain, and for online sessions the numeric user id), so any unprivileged internet user can construct a valid session ID for a target shop without ever authenticating.

### Finding Description
When OAuth completes for a non-embedded app, the cookie value is set directly to `session.id`: [1](#0-0) 

`session.id` is computed deterministically:
- Offline sessions: `"offline_#{shop}"`
- Online sessions: `"#{shop}_#{associated_user.id}"` [2](#0-1) 

The host app is documented to read this same cookie back and treat its raw value as the session identifier, with no cryptographic verification performed by the gem: [3](#0-2) [4](#0-3) 

The gem's own documentation instructs apps to store this exact `cookie.value` and later feed it back through `current_session_id`/`cookie_session_id` to retrieve the stored `Session` (containing the real `access_token`) from the app's session repository: [5](#0-4) [6](#0-5) 

This breaks the binding "session id derived from unauthenticated bytes → identity of the authenticated party". The cookie is supposed to act as proof that the browser completed OAuth for a specific shop/user, but its value carries no signature, nonce, or secret-derived component — it is fully reconstructable by anyone who knows (or guesses) the target shop's `myshopify.com` domain (public information, visible in every storefront URL) and, for online sessions, the target user's numeric ID.

Compare with the embedded-app path, which is safe: there the session id is derived only after validating a JWT signed with `Context.api_secret_key` via `JwtPayload`: [7](#0-6) 

No equivalent verification exists for the cookie path.

### Impact Explanation
An unprivileged attacker, with no access token, no `api_secret_key`, and no privileged account, can set `Cookie: shopify_app_session=offline_<victim-shop>.myshopify.com` on a request to the app and have the host application (following this gem's documented API) resolve that to the victim shop's real, persisted `Session` — including its live Shopify `access_token`. This is a cross-tenant access / access-token theft vulnerability: the attacker obtains use of another merchant's authenticated session without ever completing OAuth for that shop.

### Likelihood Explanation
High likelihood for any non-embedded app built per the documented pattern: the shop domain is always public, offline session IDs require no guessing at all (`"offline_#{shop}"`), and the gem performs zero binding/verification of the cookie's authenticity — it hands the raw cookie value straight through as the trusted session key.

### Recommendation
Do not use a deterministic, unsigned string as the bearer credential for session lookup. Either:
- Sign/MAC the cookie value (e.g., HMAC with `api_secret_key`, similar to `Utils::HmacValidator`) and verify it before using it as a lookup key, or
- Use a cryptographically random session identifier (e.g., `SecureRandom.uuid`) stored server-side and mapped internally to shop/user, instead of a value derivable purely from public shop/user identifiers.

### Proof of Concept
1. App is deployed non-embedded; victim shop `victim-shop.myshopify.com` has already completed OAuth (offline access token stored by the host app, per the documented `MyApp::SessionRepository.store_session` pattern).
2. Attacker (never having installed or authenticated to the app) sends a request to any authenticated route of the app with header:
   `Cookie: shopify_app_session=offline_victim-shop.myshopify.com`
3. Host app calls `ShopifyAPI::Utils::SessionUtils.current_session_id(nil, cookies, false)`, which returns `"offline_victim-shop.myshopify.com"` straight from the cookie with no verification (`cookie_session_id` in `lib/shopify_api/utils/session_utils.rb:68-71`).
4. Host app looks up its session store with that ID (as instructed by the gem's docs), retrieves the victim's real `Session` (with `access_token`), and the attacker's subsequent API calls now execute against the victim's shop using the victim's access token.

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

**File:** lib/shopify_api/utils/session_utils.rb (L63-71)
```ruby
        sig { params(shop: String).returns(String) }
        def offline_session_id(shop)
          "offline_#{shop}"
        end

        sig { params(cookies: T::Hash[String, String]).returns(T.nilable(String)) }
        def cookie_session_id(cookies)
          cookies[Auth::Oauth::SessionCookie::SESSION_COOKIE_NAME]
        end
```

**File:** docs/usage/oauth.md (L253-263)
```markdown
    # Update cookies with the authorized access token from result
    cookies[auth_result[:cookie].name] = {
      expires: auth_result[:cookie].expires,
      secure: true,
      http_only: true,
      value: auth_result[:cookie].value
    }

    # Store the Session object if your app has a DB/file storage for session persistence
    # This session object could be retrieved later to make authenticated API requests to Shopify
    MyApp::SessionRepository.store_session(auth_result[:session])
```

**File:** docs/getting_started.md (L47-52)
```markdown
#### Cookie
Cookie based authentication is not supported for embedded apps due to browsers dropping support for third party cookies due to security concerns. Non-embedded apps are able to use cookies for session storage/retrieval.

For *non-embedded* apps, you can pass the cookies into:
 - `ShopifyAPI::Utils::SessionUtils.current_session_id(nil, cookies, true)` for online (user) sessions or
 - `ShopifyAPI::Utils::SessionUtils.current_session_id(nil, cookies, false)` for offline (store) sessions.
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
