### Title
Cookie-based session lookup trusts the raw, unauthenticated `shopify_app_session` cookie value as the session identifier - ([File: lib/shopify_api/utils/session_utils.rb])

### Summary
For non-embedded apps, `ShopifyAPI::Utils::SessionUtils.current_session_id` derives the "current session" identity directly from the `shopify_app_session` cookie value with no cryptographic verification, while the embedded-app path derives it from a signed JWT (`session_token`). This breaks the intended equality `cookie value == value bound to a verified OAuth completion for shop S`, because the cookie branch never checks any signature/HMAC over the value it returns.

### Finding Description
`SessionUtils.current_session_id` has two code paths:
- Embedded path: extracts and validates a Shopify ID token (JWT, signed with `api_secret_key`) via `session_id_from_shopify_id_token`, producing a session id like `"#{shop}_#{sub}"` after cryptographic verification in `JwtPayload#initialize`. [1](#0-0) [2](#0-1) 

- Non-embedded / cookie fallback path: simply reads `cookies[Auth::Oauth::SessionCookie::SESSION_COOKIE_NAME]` and returns it verbatim as the session id, with zero verification that the value was produced by this gem's OAuth flow, or that it corresponds to the requester's own session: [3](#0-2) 

The value that legitimately ends up in this cookie is `session.id`, which is deterministically derived from the shop domain and (for offline sessions) contains no randomness at all — `"offline_#{shop}"`: [4](#0-3) [5](#0-4) 

The cookie is written by the host app in the OAuth callback using exactly this deterministic value and no additional signature (`cookies[auth_result[:cookie].name] = ... value: auth_result[:cookie].value`), as documented in `docs/usage/oauth.md`: [6](#0-5) 

Because `offline_#{shop}` is fully predictable from the public shop domain (e.g. `offline_some-merchant.myshopify.com`), and `SessionUtils.current_session_id` — the gem's own documented API for cookie-based session retrieval — returns this raw string unauthenticated, any actor who can place/replace this cookie in a victim's browser (e.g. via a subdomain cookie-tossing vector, a shared parent domain, or by writing it into any code path that trusts client input) can force the host app's `SessionRepository.find_session_by_id` (as documented in `docs/getting_started.md`) to hand back the stored offline access token belonging to the target shop, without the requester ever completing OAuth. [7](#0-6) 

This is the exact identity-binding failure named in the task rules: "a session id derived from unauthenticated bytes." The embedded/JWT path binds the session id to a cryptographically verified claim (`aud` checked against `Context.api_key`, `HS256` signature checked against `Context.api_secret_key`), whereas the cookie path binds it to nothing but the raw bytes the client presents.

### Impact Explanation
If the host application follows this gem's documented pattern (store/retrieve `Session` objects keyed by the id returned from `current_session_id`), an attacker who can inject this specific cookie value into a victim's request gets the app to resolve a legitimate, previously-established `Session` — including its stored offline `access_token` — for an arbitrary, attacker-chosen shop, without possessing any secret. This is a session-fixation-class identity-binding break (cross-tenant session confusion) directly attributable to this gem's own cookie-derived `current_session_id` helper providing no integrity check, in contrast to the JWT path it exposes for embedded apps.

### Likelihood Explanation
Exploitability requires the attacker to control (or force) the cookie value seen by the server for the vulnerable path — via cookie injection primitives such as subdomain cookie tossing, a response-splitting bug, or any surface where the cookie can be set cross-origin/cross-subdomain — and requires the target's offline session to already exist in storage. This is a High-likelihood design gap for merchants sharing a base domain/subdomain structure with less-trusted subdomains, but moderate-to-low in a fully isolated deployment; regardless, the root cause — unauthenticated cookie value trusted 1:1 as session id — lives entirely in this gem's `SessionUtils`.

### Recommendation
Do not trust the raw cookie value as a global session-lookup key. Bind the cookie to the request via a signed/HMAC'd cookie value (or an opaque random session identifier decoupled from the deterministic `shop`/`offline_#{shop}` naming scheme), and validate the signature in `SessionUtils.cookie_session_id`/`current_session_id` before returning it, mirroring the verification already performed for the JWT branch in `JwtPayload`.

### Proof of Concept
1. App A is installed on `victim-shop.myshopify.com` (non-embedded), completing OAuth normally; the host app persists a `Session` with `id = "offline_victim-shop.myshopify.com"` per `Session.from`. [4](#0-3) 
2. An attacker, via a cookie-injection primitive on a shared parent/subdomain (e.g. cookie tossing from `evil.victim-app-host.com` onto `victim-app-host.com`), sets `shopify_app_session=offline_victim-shop.myshopify.com` in a victim's or their own browser session against the app.
3. The app calls `ShopifyAPI::Utils::SessionUtils.current_session_id(nil, cookies, false)`, which returns the attacker-controlled string unchanged: [1](#0-0) 
4. The host app looks up `"offline_victim-shop.myshopify.com"` in its session store (per the documented pattern) and retrieves the real merchant's offline access token, activating it for subsequent Admin API calls made on the attacker's behalf.

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

**File:** lib/shopify_api/auth/jwt_payload.rb (L76-81)
```ruby
      sig { params(token: String, api_secret_key: String).returns(T::Hash[String, T.untyped]) }
      def decode_token(token, api_secret_key)
        JWT.decode(token, api_secret_key, true, leeway: JWT_LEEWAY, algorithm: "HS256")[0]
      rescue JWT::DecodeError => err
        raise ShopifyAPI::Errors::InvalidJwtTokenError, "Error decoding session token: #{err.message}"
      end
```

**File:** lib/shopify_api/auth/session.rb (L113-117)
```ruby
            associated_user_scope = access_token_response.associated_user_scope
            id = "#{shop}_#{associated_user.id}"
          else
            id = "offline_#{shop}"
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

**File:** docs/getting_started.md (L47-52)
```markdown
#### Cookie
Cookie based authentication is not supported for embedded apps due to browsers dropping support for third party cookies due to security concerns. Non-embedded apps are able to use cookies for session storage/retrieval.

For *non-embedded* apps, you can pass the cookies into:
 - `ShopifyAPI::Utils::SessionUtils.current_session_id(nil, cookies, true)` for online (user) sessions or
 - `ShopifyAPI::Utils::SessionUtils.current_session_id(nil, cookies, false)` for offline (store) sessions.
```
