### Title
Non-embedded session lookup trusts the raw, unsigned session cookie value as the session identifier - ([File: lib/shopify_api/utils/session_utils.rb])

### Summary
For non-embedded apps (and as a fallback for embedded apps without a session token), `ShopifyAPI::Utils::SessionUtils.current_session_id` returns the session cookie's value, unmodified, as the key used to fetch a merchant's stored session (and therefore its access token). The cookie value is never signed, HMAC'd, or otherwise bound to a prior authentication step by this gem, and its format is fully predictable (`"offline_#{shop}"` or `"#{shop}_#{user_id}"`).

### Finding Description
`current_session_id` decides how to identify "the current session": [1](#0-0) 

When there is no `shopify_id_token` (i.e. the common non-embedded flow, or any embedded call where the header is simply absent), it falls straight to `cookie_session_id(cookies)`: [2](#0-1) 

which just returns `cookies[SessionCookie::SESSION_COOKIE_NAME]` verbatim — the raw bytes the client sent in the `shopify_app_session` cookie become the session id used to look up the stored `Session` (and its access token) in whatever session storage the host app wires up.

Crucially, the gem itself generates this cookie value from a completely predictable, unsigned template. After OAuth completes, `Oauth.validate_auth_callback` sets the cookie to `session.id`: [3](#0-2) 

and `session.id` for the common offline case is `"offline_#{shop}"`, and for online is `"#{shop}_#{user_id}"`: [4](#0-3) 

The equality being relied on for authentication is:
`session_id used to fetch merchant's access token == raw cookie bytes supplied by the client`

But nothing binds those bytes to the fact that *this browser* completed OAuth for *that* shop — there is no HMAC, no server-side nonce comparison, and no signature check anywhere in `SessionCookie` (a plain `T::Struct` with `name`, `value`, `expires`, no signing): [5](#0-4) 

Because the shop domain (`*.myshopify.com`) is public/guessable, and the id format `offline_<shop>` is deterministic and documented, any unprivileged internet user can construct a `shopify_app_session` cookie value for an arbitrary target shop and send it to the app.

### Impact Explanation
If the host application follows this gem's documented pattern (uses `SessionUtils.current_session_id` to key its session storage and then loads the corresponding `Session`/access token to make Admin API calls on the merchant's behalf), an attacker who sets `shopify_app_session=offline_target-shop.myshopify.com` causes the app to fetch and use the victim shop's stored access token for the attacker's request — a cross-tenant access / session-fixation vulnerability (accessing another merchant's data/API using their token) without ever completing OAuth as that merchant.

### Likelihood Explanation
Requires no credentials, no secret key, and no privileged position — only knowledge/guessing of a target shop's `myshopify.com` domain (often public) and the ability to set an HTTP cookie, which any unprivileged internet user can do. The session id format is deterministic and exposed by this gem's own logic, so no brute-forcing of entropy is needed beyond guessing the shop domain.

### Recommendation
Do not use client-controlled, unsigned cookie bytes as the trust anchor for session lookups. Bind the cookie value to the authenticated session with a server-side signature/HMAC (or store only an unpredictable, high-entropy token in the cookie while keeping shop/user association strictly server-side), and verify that binding in `cookie_session_id`/`current_session_id` before using it to key the session store.

### Proof of Concept
1. Determine or guess a target Shopify store's domain, e.g. `victim-shop.myshopify.com` (store domains are frequently public).
2. As an unauthenticated attacker, send a request to the vulnerable app's non-embedded endpoint with header/cookie: `Cookie: shopify_app_session=offline_victim-shop.myshopify.com`.
3. The app calls `ShopifyAPI::Utils::SessionUtils.current_session_id(nil, cookies, false)`, which returns `"offline_victim-shop.myshopify.com"` unchanged (`lib/shopify_api/utils/session_utils.rb:19-37,68-71`).
4. The host app's session storage (built per this gem's documented pattern) looks up and returns the real `Session` object for `victim-shop.myshopify.com`, including its stored access token.
5. Subsequent API calls made by the app on behalf of "the current session" now operate with the victim shop's access token, granting the attacker cross-tenant access.

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
