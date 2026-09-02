### Title
Non-embedded OAuth session cookie value is a predictable, unsigned session identifier enabling cross-tenant session hijacking - (File: `lib/shopify_api/auth/oauth.rb`, `lib/shopify_api/utils/session_utils.rb`)

### Summary
For non-embedded apps, `ShopifyAPI::Auth::Oauth.validate_auth_callback` sets the `shopify_app_session` cookie's value to the raw `Session#id`, which is deterministically derived from the merchant's shop domain (and, for online sessions, the associated user id) rather than from any secret or signature. `ShopifyAPI::Utils::SessionUtils.cookie_session_id`/`current_session_id` then trust this raw cookie value as the session lookup key with no verification. An attacker who knows (or guesses) a target shop's domain can set this cookie value themselves and be treated as if they possess that shop's session, breaking the intended binding "cookie value == identity established via completed, HMAC-verified OAuth" down to "cookie value == arbitrary attacker-supplied bytes."

### Finding Description
In `validate_auth_callback`, after the OAuth code exchange completes, the non-embedded cookie is built directly from the deterministic session id: [1](#0-0) 

The session id itself is fully predictable, constructed only from public data: [2](#0-1) 

Nothing in the id computation depends on a secret (`api_secret_key`) or the HMAC-verified OAuth response - `offline_{shop}` for offline sessions, `{shop}_{associated_user.id}` for online sessions. Both `shop` and Shopify user ids are enumerable/guessable public information.

On the read path, the library provides (and documents) a helper that blindly trusts whatever value is present in this cookie as the authenticated session id, without any signature/HMAC check to confirm it was actually issued by this library's OAuth flow: [3](#0-2) [4](#0-3) 

This is the officially documented flow for non-embedded apps: [5](#0-4) 

The equality that should hold is: `session id trusted by the app == session id that was issued by this library after a successfully HMAC-verified OAuth callback`. Instead what actually holds is: `session id trusted by the app == unauthenticated bytes supplied in a browser cookie`, since the id is both predictable and unsigned. Any unprivileged internet user can craft this cookie value for a shop they do not control and have never authenticated as.

### Impact Explanation
If a host application follows this gem's documented pattern - storing sessions keyed by `Session#id` and retrieving them for authenticated API calls via `SessionUtils.current_session_id`/`cookie_session_id` - an attacker who sets `shopify_app_session=offline_{victim-shop}.myshopify.com` (or `{victim-shop}.myshopify.com_{user_id}` for online sessions) in their own browser will cause the app to look up and use the victim shop's stored access token for subsequent Admin API requests made on the attacker's behalf. This is cross-tenant access to another merchant's data using their access token, without the attacker ever needing to know `api_secret_key`, a leaked token, or perform any privileged action - only the (public) shop domain.

### Likelihood Explanation
Likelihood is high wherever this gem's documented cookie-based session lookup is used for non-embedded apps: the shop domain is public/known to the attacker (e.g., it's the app's own installer, or discoverable), and Shopify numeric user ids are small, enumerable integers. No cryptographic secret is required to construct a valid-looking cookie value, since the value contains no signature or nonce tying it to a specific completed OAuth handshake.

### Recommendation
Do not use a deterministic, information-derived string as the literal cookie value trusted for session lookup. Instead, generate an unguessable, random session-cookie value at OAuth completion (e.g., a `SecureRandom` token, or an HMAC/signed value binding the session id to a secret) and store/retrieve the actual `Session#id` server-side keyed by that random value, or verify the incoming cookie value with an HMAC/signature check before treating it as authoritative in `SessionUtils.cookie_session_id`.

### Proof of Concept
1. App is configured non-embedded; a real merchant `victim-shop.myshopify.com` completes OAuth, and the host stores a `ShopifyAPI::Auth::Session` with `id: "offline_victim-shop.myshopify.com"` per `Session.from`.
2. Attacker, in their own unauthenticated browser session, manually sets the browser cookie:
   `shopify_app_session=offline_victim-shop.myshopify.com`
3. Attacker requests any authenticated route of the app that calls
   `ShopifyAPI::Utils::SessionUtils.current_session_id(nil, cookies, false)`.
4. Per `cookie_session_id`, the raw attacker-supplied cookie value is returned unchecked as the trusted session id: [4](#0-3) .
5. The host application's session repository looks up and returns the stored `Session` for `victim-shop.myshopify.com`, and the app makes Admin API calls using the victim's access token on the attacker's behalf - cross-tenant access achieved with zero secrets.

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

**File:** lib/shopify_api/utils/session_utils.rb (L68-71)
```ruby
        sig { params(cookies: T::Hash[String, String]).returns(T.nilable(String)) }
        def cookie_session_id(cookies)
          cookies[Auth::Oauth::SessionCookie::SESSION_COOKIE_NAME]
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
