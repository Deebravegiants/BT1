### Title
Cross-tenant session hijack via unauthenticated, predictable non-embedded session cookie value - ([File: lib/shopify_api/utils/session_utils.rb])

### Summary
For non-embedded apps (and as a fallback for embedded apps without a JWT), `ShopifyAPI::Utils::SessionUtils.current_session_id` returns the session identifier used by the host application to look up a stored `Session` (and its access token) directly from the raw `shopify_app_session` cookie value, with no cryptographic binding to the requester's identity.

### Finding Description
`SessionUtils.current_session_id` has two code paths: a JWT path that cryptographically validates the caller's identity via `Auth::JwtPayload` (HS256-signed with `api_secret_key`), and a cookie fallback path that simply echoes back whatever the browser sent: [1](#0-0) [2](#0-1) 

The value stored in that cookie is set, once, at the end of OAuth to the raw session id string — `"offline_#{shop}"` for offline sessions or `"#{shop}_#{associated_user.id}"` for online sessions — with no signature, MAC, or encryption applied by this gem: [3](#0-2) [4](#0-3) [5](#0-4) 

The identity binding that should hold is: `session id returned to the host application == session id cryptographically derived from a validated shop/user identity`. Instead, for the cookie path the equality actually enforced is: `session id returned == raw bytes supplied by the client`, with no proof those bytes originated from Shopify or from this browser's own OAuth flow. Because the offline session id is deterministically `"offline_" + shop_domain`, and shop domains (`*.myshopify.com`) are public/guessable identifiers (visible in storefront URLs, app listings, etc.), any unauthenticated user can compute a victim merchant's session id without ever completing OAuth for that shop.

### Impact Explanation
If a host application follows the gem's documented pattern (`current_session_id` → look up stored `Session` → use its `access_token` to call the Admin API on the caller's behalf, as shown in `docs/usage/oauth.md`), an attacker who sets their own browser's `shopify_app_session` cookie to `"offline_<victim-shop>.myshopify.com"` causes the host app to resolve and act using the victim merchant's session/access token. This is cross-tenant access: an unprivileged user obtains use of another shop's stored offline access token purely by guessing/knowing that shop's domain, without ever possessing the `api_secret_key`, the shop's access token, or performing the OAuth flow for that shop.

### Likelihood Explanation
Exploitation requires only a normal browser and knowledge of the target's `myshopify.com` domain — no secrets, no privileged access, no TLS interception. The session id format is fixed and documented (`offline_#{shop}`, `#{shop}_#{user_id}`), so an attacker does not need to observe an actual cookie value; they can construct it themselves. The only precondition is that the host app stores/serves the offline session for that shop (true for any installed app) and that it uses the gem's documented `current_session_id` API for non-embedded or JWT-less requests, which is the gem's own primary intended usage pattern, not a misuse of it.

### Recommendation
Do not treat the raw cookie value as a trusted, resolvable session identifier. Either (a) bind the cookie value to a server-verifiable secret (e.g., HMAC/sign the cookie contents with `api_secret_key`/a random per-session secret and verify it in `cookie_session_id` before returning it), or (b) store an unguessable random session id (already generated as `SecureRandom.uuid` in `Auth::Session#initialize`) as the cookie's public identifier instead of the deterministic `offline_#{shop}` / `#{shop}_#{user_id}` string, and require the caller-visible id to be looked up only via the signed cookie, never derivable from public shop names alone.

### Proof of Concept
1. Attacker learns/guesses a victim merchant's `myshopify.com` domain, e.g. `victim-shop.myshopify.com` (public information).
2. App previously completed offline OAuth for that shop, so the host application's session store contains a `Session` with `id: "offline_victim-shop.myshopify.com"` and a valid `access_token`.
3. Attacker sends a request to the host app (non-embedded route, or embedded route without a `shopify_id_token`) with cookie:
   `shopify_app_session=offline_victim-shop.myshopify.com`
4. Host app calls `ShopifyAPI::Utils::SessionUtils.current_session_id(nil, cookies, false)`, which returns `"offline_victim-shop.myshopify.com"` unchanged. [6](#0-5) 
5. Host app loads the corresponding `Session` from storage using this id and uses its `access_token` for the request, executing Admin API calls as the victim shop on the attacker's behalf.

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
