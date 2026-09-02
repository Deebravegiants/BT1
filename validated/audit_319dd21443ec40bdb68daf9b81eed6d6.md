### Title
Session ID Trusted from Unsigned, Predictable Cookie Value Enables Cross-Tenant Session Fixation - (File: `lib/shopify_api/utils/session_utils.rb`)

### Summary
For non-embedded apps (and as an embedded fallback), `ShopifyAPI::Utils::SessionUtils.current_session_id` resolves the "current session" identity directly from the raw bytes of the `shopify_app_session` cookie, with no cryptographic binding proving that value was actually issued by this gem's OAuth flow to this browser.

### Finding Description
When OAuth completes, `ShopifyAPI::Auth::Oauth.validate_auth_callback` builds the browser cookie as the plaintext session identifier itself: [1](#0-0) 

`SessionCookie` is a plain struct holding this value with no HMAC or signature over it: [2](#0-1) 

Later, when resolving "who is calling", `SessionUtils.cookie_session_id` simply reads that cookie value back out and treats it as the authenticated session key, with no HMAC/signature check comparable to the one applied elsewhere in this same codebase (e.g. `Utils::HmacValidator.validate` used for OAuth callbacks and webhooks): [3](#0-2) [4](#0-3) 

Critically, the session ID format is deterministic and derived from public information: [5](#0-4) 

- Offline session id: `"offline_#{shop}"`
- Online session id: `"#{shop}_#{user_id}"`

`shop` is simply the merchant's `*.myshopify.com` domain (public/guessable), and `user_id` values are typically small sequential integers. This breaks the identity binding that should hold:

`session_id trusted by the gem == session_id cryptographically proven to have been minted by Shopify's OAuth callback for this specific browser`

Instead it degrades to:

`session_id trusted by the gem == whatever bytes are present in a cookie named shopify_app_session`

Unlike the JWT-based path (`session_id_from_shopify_id_token`), which derives the session id only after `JwtPayload` verifies an HMAC-signed token from Shopify, the cookie path performs **no equivalent verification** — the gem itself constructs and later trusts an unauthenticated, guessable value as if it were an authenticated credential.

### Impact Explanation
This is a session-fixation / cross-tenant identity confusion primitive supplied directly by the gem's own API, not something requiring the host app to misuse or ignore documented behavior — the vulnerable value (`session.id`) and its unauthenticated read-back (`cookie_session_id`) are both implemented inside `shopify_api`. Any host app that follows the documented non-embedded cookie flow (`docs/getting_started.md` "Cookie" section, lines 47-52) inherits this weakness: an attacker who can set a cookie in the victim's browser for the app's domain (e.g. via response header injection, a related subdomain, or simply by predicting/guessing the deterministic ID and using it directly against their own authenticated session with the app) can cause the host app to resolve and act under another shop's/user's session identifier, since the value itself carries no proof of provenance. This lets the identity boundary between tenants be crossed via forged/predicted session identifiers, matching the "session fixation" / identity-binding-bypass class called out for this scan.

### Likelihood Explanation
Every non-embedded integration that follows the documented `current_session_id(nil, cookies, ...)` path is affected, since the vulnerable code path is the library's own recommended usage, not a misuse of it. Constructing a target session id requires only public information (the shop's `myshopify.com` domain) and, for online sessions, a small enumerable user id — no secret material is needed to construct the string; only the ability to place it as a cookie value is needed.

### Recommendation
Do not use the raw session identifier as the cookie's contents. Instead, either (a) sign/HMAC the cookie value with `api_secret_key` (mirroring `Utils::HmacValidator`) and verify that signature in `cookie_session_id` before trusting it, or (b) store a random, unguessable, server-side-mapped token in the cookie instead of the deterministic `shop`/`shop_user_id` string, so possession of the cookie — not knowledge of a predictable identifier — is what proves session ownership.

### Proof of Concept
1. Note that for a target shop `victim-shop.myshopify.com`, the offline session id is always `offline_victim-shop.myshopify.com` (`lib/shopify_api/utils/session_utils.rb`, `offline_session_id`), and for an online session with user id `12345` it is `victim-shop.myshopify.com_12345` (`jwt_session_id`).
2. An attacker who can write a cookie for the app's domain (e.g., via a header-injection bug in a subdomain, a shared parent domain, or by simply supplying the cookie header directly when calling the host app's session-loading logic in a non-browser context) sets:
   `Cookie: shopify_app_session=offline_victim-shop.myshopify.com`
3. The host app calls `ShopifyAPI::Utils::SessionUtils.current_session_id(nil, cookies, false)`, which returns `"offline_victim-shop.myshopify.com"` unchanged (`session_utils.rb` lines 31-36, `cookie_session_id` lines 68-71) — no verification step rejects it.
4. The host app looks up its stored `Session` for that id and uses the associated (real) access token to make Admin API calls on the attacker's behalf, achieving cross-tenant access without ever possessing a legitimately-issued cookie.

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

**File:** lib/shopify_api/utils/session_utils.rb (L58-71)
```ruby
        sig { params(shop: String, user_id: String).returns(String) }
        def jwt_session_id(shop, user_id)
          "#{shop}_#{user_id}"
        end

        sig { params(shop: String).returns(String) }
        def offline_session_id(shop)
          "offline_#{shop}"
        end

        sig { params(cookies: T::Hash[String, String]).returns(T.nilable(String)) }
        def cookie_session_id(cookies)
          cookies[Auth::Oauth::SessionCookie::SESSION_COOKIE_NAME]
        end
```
