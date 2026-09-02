### Title
Predictable, unsigned offline session ID used as session cookie value enables session fixation / cross-tenant session hijacking - (File: `lib/shopify_api/auth/session.rb`, `lib/shopify_api/utils/session_utils.rb`, `lib/shopify_api/auth/oauth.rb`)

### Summary
For non-embedded (cookie-based) apps, the gem sets the session cookie to the raw session `id` returned by OAuth, and later trusts whatever value is present in that cookie as the session identifier with no cryptographic binding. For offline sessions, that `id` is not random — it is the deterministic string `"offline_#{shop}"`. This breaks the intended equality `session id in cookie == identifier of a session this specific browser actually completed OAuth for`; instead the check degenerates to `session id in cookie == "offline_" + any shop name`, which any client can compute or guess.

### Finding Description
`ShopifyAPI::Auth::Session.from` builds the session `id` for offline (store-level) sessions purely from the shop domain, with no random or secret component: [1](#0-0) 

The same deterministic pattern is exposed directly as a helper: [2](#0-1) 

After a successful (non-embedded) OAuth callback, this predictable `id` is written verbatim into the session cookie value, with no HMAC or signature over it: [3](#0-2) 

On every subsequent request, `SessionUtils.current_session_id` (and `cookie_session_id`) reads the cookie value and hands it back as *the* session id to be used for looking up the stored session/access token, performing no verification that this value was actually issued by this library for this browser: [4](#0-3) [5](#0-4) 

The documentation confirms this is the intended, supported flow for non-embedded apps: the cookie value returned by `current_session_id` is meant to be used directly to look up the persisted session (access token) in the host app's storage: [6](#0-5) 

The binding this breaks, stated as an equality:
`identity the app authenticated via OAuth for shop S` **should equal** `identity the app looks up via SessionUtils.current_session_id`, but instead the latter equals `raw, unsigned cookie bytes`, and for offline sessions those bytes are the fully predictable string `"offline_" + shop_domain` — something any user of the gem (including an attacker who is simply another merchant/installer of the same app, or anyone able to influence the victim's cookie jar for the app's domain) can compute without ever authenticating as that shop.

### Impact Explanation
Because the session identifier is both (a) unsigned/unverified and (b) trivially predictable for offline sessions, an attacker who can place this cookie in a victim's browser (e.g., classic session fixation via response/header cookie injection, a shared/proxy caching bug, or a sibling subdomain writing the cookie) — or who can simply cause their own client to present the crafted cookie to a host app whose backend trusts `current_session_id` as an authorization key — can cause the host application to retrieve and act using another tenant's stored offline access token. This is a cross-tenant session/session-fixation issue matching the "High" impact category (session fixation) and, if the host's storage returns the token itself for use, escalates to token/credential exposure across tenants.

### Likelihood Explanation
Likelihood is High for apps that follow the documented, supported non-embedded cookie flow: `SessionUtils.current_session_id(nil, cookies, false)` is the library's own documented API for this case, and it performs no validation of the cookie's authenticity — it is pure pass-through of attacker-influenced bytes, and the offline `id` format (`"offline_" + shop`) is public/documented (`Session.from`), removing any need to brute force or leak it.

### Recommendation
- Do not use a deterministic, unsigned value (`"offline_#{shop}"`) as a bearer-style session cookie value. Sign/HMAC the cookie value (or wrap it in a signed token) so `cookie_session_id` can verify integrity/authenticity before returning it.
- Alternatively, mint a random, non-guessable session id for offline sessions (as is already done implicitly for embedded/online sessions via JWT-derived ids) and bind the cookie value to that random id rather than the shop name.
- Document clearly that host applications must not treat the returned `current_session_id` as authoritative without additional binding (e.g., re-validating shop ownership) if they choose to persist it as a lookup key.

### Proof of Concept
1. Merchant `victim-shop.myshopify.com` installs the app (non-embedded); OAuth completes and the app sets cookie `shopify_session_id = "offline_victim-shop.myshopify.com"` per `Oauth.validate_auth_callback` / `Session.from`.
2. Attacker, without ever completing OAuth for `victim-shop`, computes the same deterministic id (`"offline_" + "victim-shop.myshopify.com"`) since the format is fixed and shop domains are often discoverable/public.
3. Attacker sets this value as their own session cookie (or fixates it into a victim's browser via a cookie-injection vector on the app's domain) and calls the host app's endpoints.
4. The host app calls `ShopifyAPI::Utils::SessionUtils.current_session_id(nil, cookies, false)`, which returns the attacker-supplied `"offline_victim-shop.myshopify.com"` unchecked, and the host app looks this id up in its session store, retrieving `victim-shop`'s persisted offline session/access token for use on the attacker's request.

### Citations

**File:** lib/shopify_api/auth/session.rb (L114-117)
```ruby
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

**File:** docs/getting_started.md (L47-53)
```markdown
#### Cookie
Cookie based authentication is not supported for embedded apps due to browsers dropping support for third party cookies due to security concerns. Non-embedded apps are able to use cookies for session storage/retrieval.

For *non-embedded* apps, you can pass the cookies into:
 - `ShopifyAPI::Utils::SessionUtils.current_session_id(nil, cookies, true)` for online (user) sessions or
 - `ShopifyAPI::Utils::SessionUtils.current_session_id(nil, cookies, false)` for offline (store) sessions.

```
