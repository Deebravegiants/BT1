### Title
Session ID Cookie Value Is a Predictable, Unsigned Identifier Used Directly for Session Lookup - ([File: lib/shopify_api/auth/oauth.rb](), [File: lib/shopify_api/utils/session_utils.rb](), [File: lib/shopify_api/auth/session.rb]())

### Summary
For non-embedded apps, the OAuth callback flow sets a browser cookie whose *value* is literally the deterministic session id (`shop_userid` or `offline_shop`), with no signature, MAC, or encryption. `SessionUtils.cookie_session_id` later returns this raw cookie value verbatim to be used as the storage lookup key for the `Session` object (and thus the merchant's access token). This breaks the intended binding "cookie presented by browser == proof of a previously-authenticated OAuth session for that browser," because the cookie's bytes carry no authentication of their own — they are just a copy of a predictable identifier.

### Finding Description
`Session.from` derives the session `id` purely from public/guessable values: [1](#0-0) 

For non-embedded (non-`Context.embedded?`) apps, `Oauth.validate_auth_callback` sets the browser session cookie's `value` directly to this `session.id`: [2](#0-1) 

`SessionCookie` is a plain struct with no signing/HMAC of its own: [3](#0-2) 

Downstream, `SessionUtils.current_session_id`/`cookie_session_id` take whatever value is present in the `shopify_app_session` cookie and return it unmodified as the session id to be used for storage lookup — with no verification that this value was ever actually issued by this gem's OAuth flow: [4](#0-3) [5](#0-4) 

The identity binding that should hold is: *`cookie value` presented by an unauthenticated browser request == a value only obtainable by having actually completed OAuth as that user/shop*. Instead the binding that actually holds is: *`cookie value` == `"#{shop}_#{shopify_user_id}"` or `"offline_#{shop}"`*, both of which are either public (the shop's `myshopify.com` domain, visible in the app URL/`dest` JWT claim) or a small, often sequential, numeric Shopify user/customer id. Because the cookie is not cryptographically bound to a specific browser session or nonce, any party who can guess or learn a target's `shop` + numeric user id can construct the exact cookie value that the legitimate flow would have produced, without ever having gone through OAuth or possessing an access token.

### Impact Explanation
If a host application follows this gem's documented pattern verbatim — storing `auth_result[:cookie]` in the browser and later calling `SessionUtils.current_session_id`/`cookie_session_id` to fetch the `Session`/access token from its session store keyed by that same id — then an attacker who sets their own browser's `shopify_app_session` cookie to a guessed value (`"targetshop.myshopify.com_1"`, `"targetshop.myshopify.com_2"`, ... or `"offline_targetshop.myshopify.com"`) can have the app load and act as the victim's session, i.e. use the victim's stored offline/online access token for API calls made "on behalf of" the attacker's request. This is a session-fixation/hijack primitive that leads to cross-tenant or cross-user access to a merchant's access token-backed session without ever authenticating — matching the High-severity "session fixation" and "credential/session binding bypass" categories.

### Likelihood Explanation
Exploitability depends on: (1) the app being non-embedded (the code path that sets the plaintext id as the cookie value), (2) the app relying on `SessionUtils.cookie_session_id`/`current_session_id` (the gem's own documented helper) as the sole trust anchor for session retrieval, and (3) the attacker being able to guess/know a target shop's numeric user id (often low-entropy/sequential for early Shopify accounts) or targeting the offline (store-level) session, which requires no per-user guessing at all — just knowledge of the shop's `myshopify.com` domain, which is public. This is a realistic, low-skill attack path for the offline-session case since `"offline_#{shop}"` has zero secret entropy at all.

### Recommendation
Do not use the deterministic `Session#id` (`shop_userid` / `offline_shop`) as the literal cookie value. Instead, generate an unguessable, random session token (e.g., `SecureRandom.uuid`) for the cookie, and store a server-side mapping from that random token to the real `Session` id, or sign/HMAC the cookie value using `Context.api_secret_key` so tampering/guessing can be detected before it is used as a storage key. `SessionUtils.cookie_session_id` should reject cookie values that do not carry a valid signature rather than passing through whatever byte string was received.

### Proof of Concept
1. App is configured as non-embedded (`is_embedded: false`).
2. Victim shop `victim-shop.myshopify.com` installs the app and completes OAuth once (offline token) — this is a normal legitimate install, not attacker-controlled.
3. Attacker, with no credentials, sets their own browser cookie:
   `shopify_app_session=offline_victim-shop.myshopify.com`
4. App's host code calls `ShopifyAPI::Utils::SessionUtils.current_session_id(nil, cookies, false)` per the documented pattern in `docs/getting_started.md` lines 50–52, which returns `"offline_victim-shop.myshopify.com"` verbatim. [6](#0-5) 
5. The app looks up the `Session` (and its `access_token`) by that id from its session store and uses it for subsequent API calls, effectively letting the attacker ride on the victim shop's offline access token/session with zero authentication of their own.

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
