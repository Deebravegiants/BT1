### Title
Session ID trusted from unsigned, predictable cookie value enables cross-tenant session hijacking - ([File: lib/shopify_api/utils/session_utils.rb])

### Summary
For non-embedded apps (and as an embedded fallback), `ShopifyAPI::Utils::SessionUtils.current_session_id` derives the "current session" identifier directly and exclusively from the raw `shopify_app_session` cookie value, with no cryptographic verification that the value was actually issued by the server to that browser. Because the session id the gem itself assigns to that cookie is a deterministic, non-secret string (`offline_#{shop}` or `#{shop}_#{user_id}`), any unauthenticated party who can set/send this cookie can make the host application resolve and use another tenant's stored session.

### Finding Description
`ShopifyAPI::Auth::Oauth.validate_auth_callback` sets the browser session cookie's value to `session.id`: [1](#0-0) 

The `Session#id` values produced by the gem are fully deterministic and derived only from public/guessable data — the shop domain for offline sessions, and shop + user id for online sessions: [2](#0-1) 

When resolving "the current session" for a request, `cookie_session_id` simply returns whatever value is present in the `shopify_app_session` cookie, unmodified and unverified: [3](#0-2) [4](#0-3) 

There is no HMAC, signature, or nonce binding this cookie value to a specific authenticated OAuth completion — contrast this with the `state` cookie used during the OAuth callback, which the gem does explicitly compare against the signed `auth_query.state` value: [5](#0-4) 

No such check exists for the long-lived session cookie. The identity binding broken is:

`session id trusted by cookie_session_id(cookies)` **should equal** `session id that the server actually and verifiably issued to this specific browser after OAuth`

but instead the gem accepts any bytes present under the `shopify_app_session` cookie key as a valid session id, with the only "proof" being that the id happens to match the deterministic format `offline_#{shop}` / `#{shop}_#{user_id}`.

Per `docs/getting_started.md`, this `current_session_id` API is the gem's documented, intended mechanism for non-embedded apps to resolve which stored `Session` (and thus access token) to use for API calls — so a host application using the gem exactly as documented (pass cookies in, get back a session id, look up session in storage by that id) inherits this weakness without doing anything wrong: [6](#0-5) 

### Impact Explanation
Because `offline_#{shop}` requires only knowledge of the target's `myshopify.com` domain (public/discoverable), an attacker can construct the exact cookie value that resolves to a targeted merchant's offline session id. If the attacker can get this cookie value associated with their own request (e.g. sending a raw `Cookie` header, or via any mechanism that allows cookie injection/fixation on the app's origin), the host application — following the gem's own documented pattern — will look up and use the victim merchant's stored `Session`, including its `access_token`, to serve the attacker's request. This is cross-tenant access to another merchant's session/access token, which meets the Critical impact bar (theft/use of a merchant access token, cross-tenant access) defined in scope.

### Likelihood Explanation
Exploitation requires the attacker to know/guess the shop domain (for offline sessions) or shop+user id (for online sessions) and to be able to present that value as the `shopify_app_session` cookie on a request to the vulnerable app — a low bar compared to needing `api_secret_key` or an access token. The vulnerability is in the gem's own code path (`SessionUtils.cookie_session_id`/`current_session_id`) that host apps are told to rely on directly, not a misuse of an undocumented API.

### Recommendation
Do not trust the raw cookie value as a lookup key for session storage without cryptographic binding. Either:
- Sign/HMAC the session cookie value (or wrap it in a signed cookie jar) so that `cookie_session_id` can verify the value was issued by the server before returning it, or
- Make session ids include an unguessable, per-session secret component (not just `shop` / `shop_user_id`) so they cannot be forged or predicted from public information, and validate that secret against server-side state before trusting it to resolve a stored session.

### Proof of Concept
1. Attacker learns/guesses a target merchant's shop domain, e.g. `victim-shop.myshopify.com` (public knowledge for many stores).
2. Attacker computes the expected offline session id: `offline_victim-shop.myshopify.com` (per `SessionUtils.offline_session_id`).
3. Attacker sends a request to the vulnerable (non-embedded) app with `Cookie: shopify_app_session=offline_victim-shop.myshopify.com`.
4. The app calls `ShopifyAPI::Utils::SessionUtils.current_session_id(nil, cookies, false)` as documented, which returns `"offline_victim-shop.myshopify.com"` with no verification.
5. The host app looks up the stored `Session` for that id (per the gem's documented storage pattern) and uses its `access_token` to serve the attacker's request — granting the attacker access to the victim merchant's data/session.

### Citations

**File:** lib/shopify_api/auth/oauth.rb (L67-71)
```ruby
          state = cookies[SessionCookie::SESSION_COOKIE_NAME]
          raise Errors::NoSessionCookieError unless state

          raise Errors::InvalidOauthError,
            "Invalid state in OAuth callback." unless state == auth_query.state
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

**File:** docs/getting_started.md (L47-52)
```markdown
#### Cookie
Cookie based authentication is not supported for embedded apps due to browsers dropping support for third party cookies due to security concerns. Non-embedded apps are able to use cookies for session storage/retrieval.

For *non-embedded* apps, you can pass the cookies into:
 - `ShopifyAPI::Utils::SessionUtils.current_session_id(nil, cookies, true)` for online (user) sessions or
 - `ShopifyAPI::Utils::SessionUtils.current_session_id(nil, cookies, false)` for offline (store) sessions.
```
